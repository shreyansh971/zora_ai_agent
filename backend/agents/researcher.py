# backend/agents/researcher.py
# Researcher Agent — searches academic sources
# Uses Groq first for query generation, falls back to Gemini

import os
import hashlib
import asyncio
import logging
import requests
import arxiv
from bs4 import BeautifulSoup
from typing import List, Optional
from duckduckgo_search import DDGS
from backend.models import Source

logger = logging.getLogger("zora.researcher")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _clean_text(html: str, max_words: int = 500) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ", strip=True).split()[:max_words])


def _scrape_url(url: str) -> Optional[str]:
    try:
        resp = requests.get(f"https://r.jina.ai/{url}", timeout=10, headers={"Accept": "text/plain"})
        if resp.status_code == 200 and len(resp.text) > 100:
            return " ".join(resp.text.split()[:500])
    except Exception:
        pass
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code in (401, 403):
            return None
        return _clean_text(resp.text)
    except Exception as e:
        logger.error(f"Scrape failed for {url}: {e}")
        return None


def _search_duckduckgo(query: str, max_results: int = 5) -> List[dict]:
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({"url": r.get("href",""), "title": r.get("title","Untitled"), "snippet": r.get("body","")})
    except Exception as e:
        logger.error(f"DuckDuckGo failed: {e}")
    return results


def _search_serpapi(query: str, max_results: int = 5) -> List[dict]:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return _search_duckduckgo(query, max_results)
    try:
        resp = requests.get("https://serpapi.com/search",
            params={"q": query, "engine": "google_scholar", "api_key": api_key, "num": max_results}, timeout=15)
        return [{"url": r.get("link",""), "title": r.get("title","Untitled"), "snippet": r.get("snippet","")}
                for r in resp.json().get("organic_results", [])[:max_results]]
    except Exception:
        return _search_duckduckgo(query, max_results)


def _search_arxiv(query: str, max_results: int = 3) -> List[dict]:
    results = []
    try:
        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        for paper in client.results(search):
            results.append({
                "url": paper.entry_id, "title": paper.title,
                "snippet": paper.summary[:300],
                "author": ", ".join(str(a) for a in paper.authors[:2]),
                "date": str(paper.published.year) if paper.published else "Unknown",
            })
    except Exception as e:
        logger.error(f"ArXiv failed: {e}")
    return results


def _generate_queries(topic: str) -> List[str]:
    """Generate smart queries using Groq or Gemini, fallback to templates."""
    prompt = f"""Generate 4 academic search queries for: "{topic}"
Return ONLY a JSON array: ["query1", "query2", "query3", "query4"]"""
    try:
        import json
        if GROQ_API_KEY:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": [{"role":"user","content":prompt}], "temperature":0.3, "max_tokens":150},
                timeout=15,
            )
            if resp.status_code == 200:
                text = resp.json()["choices"][0]["message"]["content"].strip()
                text = text.replace("```json","").replace("```","").strip()
                result = json.loads(text)
                if isinstance(result, list) and len(result) >= 2:
                    return result[:4]
    except Exception as e:
        logger.warning(f"Query generation failed: {e}")

    base = topic.strip().rstrip(".")
    return [f"{base} research study", f"{base} academic review", f"{base} evidence analysis", f"{base} scholarly findings"]


async def run_researcher(topic: str, on_progress=None) -> List[Source]:
    sources, seen_urls = [], set()

    if on_progress:
        on_progress(f"Generating smart search queries for: '{topic}'")

    queries = _generate_queries(topic)
    if on_progress:
        on_progress(f"Generated {len(queries)} queries")

    arxiv_results = _search_arxiv(topic, max_results=3)
    if on_progress:
        on_progress(f"Found {len(arxiv_results)} results on ArXiv")

    web_results = _search_serpapi(queries[0], max_results=5)
    if on_progress:
        on_progress(f"Found {len(web_results)} web results")

    for idx, raw in enumerate((arxiv_results + web_results)[:8]):
        url = raw.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        if on_progress:
            on_progress(f"Scraping source {idx+1}: {raw.get('title', url)[:60]}...")

        content = raw.get("snippet", "")
        if "arxiv.org" not in url:
            scraped = await asyncio.get_event_loop().run_in_executor(None, _scrape_url, url)
            if scraped:
                content = scraped

        if not content or len(content) < 30:
            continue

        sources.append(Source(
            id=f"S{len(sources)+1}", url=url,
            title=raw.get("title", "Untitled"),
            author=raw.get("author", "Unknown"),
            date=raw.get("date", "Unknown"),
            content_hash=_hash(content),
            summary=content[:500],
            reliability_score=0.9 if "arxiv.org" in url else 0.7,
        ))
        if len(sources) >= 5:
            break

    if on_progress:
        on_progress(f"Research complete. {len(sources)} sources collected.")
    return sources
