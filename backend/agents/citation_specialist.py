# backend/agents/citation_specialist.py
# Citation Specialist — generates APA citations + final draft
# Uses Groq first (fast, free), falls back to Gemini

import os
import logging
import requests
from typing import List, Optional
from backend.models import Source, VerificationChunk

logger = logging.getLogger("zora.citation")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_apa_citation(source: Source) -> str:
    author = source.author if source.author and source.author != "Unknown" else "Unknown Author"
    year = source.date if source.date and source.date != "Unknown" else "n.d."
    return f"{author}. ({year}). {source.title}. Retrieved from {source.url}"


def generate_bibliography(sources: List[Source]) -> List[str]:
    return [generate_apa_citation(s) for s in sources]


def _call_groq(prompt: str) -> str:
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 1000,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        raise Exception(f"Groq error {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def _call_gemini(prompt: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    for model_name in ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash-latest"]:
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config=genai.types.GenerationConfig(temperature=0.3),
            )
            return model.generate_content(prompt).text.strip()
        except Exception as e:
            logger.warning(f"Gemini model {model_name} failed: {e}")
    raise Exception("All Gemini models failed.")


def _generate(prompt: str) -> str:
    """Try Groq first, fallback to Gemini."""
    if GROQ_API_KEY:
        try:
            return _call_groq(prompt)
        except Exception as e:
            logger.warning(f"Groq failed, trying Gemini: {e}")
    if GEMINI_API_KEY:
        return _call_gemini(prompt)
    raise Exception("No API key found. Add GROQ_API_KEY or GEMINI_API_KEY to .env")


async def generate_final_draft(
    topic: str,
    sources: List[Source],
    draft_text: Optional[str],
    verification_log: List[VerificationChunk],
    on_progress=None,
) -> str:
    if on_progress:
        on_progress("Compiling final grounded research draft...")

    source_summaries = "\n\n".join(
        f"[{s.id}] {s.title} — {s.summary[:300]}" for s in sources
    )

    if draft_text:
        issues = [
            f"- CLAIM: '{v.chunk}' → STATUS: {v.status}"
            + (f" → SUGGESTION: {v.suggestion}" if v.suggestion else "")
            for v in verification_log if v.status != "Verified"
        ]
        issues_text = "\n".join(issues) if issues else "No issues found."

        prompt = f"""You are an academic writing assistant. Improve the student's draft by correcting hallucinations.

TOPIC: {topic}

VERIFIED SOURCES:
{source_summaries}

ISSUES FOUND IN DRAFT:
{issues_text}

ORIGINAL DRAFT:
{draft_text}

Write an improved version that:
1. Fixes any hallucinations using the actual sources
2. Cites sources inline as [S1], [S2], etc.
3. Maintains the student's original voice and structure
4. Uses formal academic language

Return ONLY the improved draft text."""
    else:
        prompt = f"""Write a well-structured academic summary on: "{topic}"

Use ONLY the following verified sources. Cite them inline as [S1], [S2], etc.:

{source_summaries}

Requirements:
- 3-4 paragraphs
- Every claim must reference a source
- Formal academic tone
- End with a brief conclusion

Return ONLY the essay text."""

    try:
        return _generate(prompt)
    except Exception as e:
        logger.error(f"Draft generation failed: {e}")
        return draft_text or f"Draft generation failed: {str(e)}\n\nPlease check your GROQ_API_KEY or GEMINI_API_KEY in .env"
