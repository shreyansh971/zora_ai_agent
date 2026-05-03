# backend/agents/verifier.py
# Verifier Agent — anti-hallucination engine
# Uses Groq first, falls back to Gemini

import re
import os
import logging
import requests
from typing import List, Callable, Optional

from backend.models import VerificationChunk
from backend.tools.vector_store import retrieve_similar

logger = logging.getLogger("zora.verifier")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _split_into_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    merged, buffer = [], ""
    for s in sentences:
        if len(s.split()) < 10 and buffer:
            buffer += " " + s
        else:
            if buffer:
                merged.append(buffer)
            buffer = s
    if buffer:
        merged.append(buffer)
    return [s for s in merged if len(s.strip()) > 5]


def _call_groq(prompt: str) -> dict:
    import json
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 200,
        },
        timeout=20,
    )
    if resp.status_code != 200:
        raise Exception(f"Groq error: {resp.status_code}")
    text = resp.json()["choices"][0]["message"]["content"].strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def _call_gemini(prompt: str) -> dict:
    import json
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    for model_name in ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash-latest"]:
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    response_mime_type="application/json",
                ),
            )
            text = model.generate_content(prompt).text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            logger.warning(f"Gemini {model_name} failed: {e}")
    raise Exception("All Gemini models failed.")


def _verify_sentence(sentence: str, context_chunks: List[dict]) -> tuple:
    if not context_chunks:
        return "Unverifiable", 0.0, "No sources found for this claim."

    source_context = "\n\n".join(
        f"[Source {c['source_id']}] ({c['title']}): {c['content']}"
        for c in context_chunks
    )

    prompt = f"""You are a strict academic fact-checker.

STUDENT'S CLAIM: "{sentence}"

AVAILABLE SOURCES:
{source_context}

Does any source support the student's claim?
Respond with JSON only (no markdown):
{{"verdict": "TRUE or PARTIAL or FALSE", "confidence": 0.0 to 1.0, "suggestion": "correction or null"}}

- TRUE = directly supported
- PARTIAL = related but not exact; provide correction
- FALSE = contradicts or absent from sources"""

    try:
        if GROQ_API_KEY:
            try:
                result = _call_groq(prompt)
            except Exception as e:
                logger.warning(f"Groq verifier failed: {e}")
                result = _call_gemini(prompt)
        else:
            result = _call_gemini(prompt)

        verdict = str(result.get("verdict", "FALSE")).upper()
        confidence = float(result.get("confidence", 0.5))
        suggestion = result.get("suggestion")
        if suggestion in ("null", "", None): suggestion = None
        status_map = {"TRUE": "Verified", "PARTIAL": "Partial", "FALSE": "Hallucinated"}
        return status_map.get(verdict, "Unverifiable"), confidence, suggestion
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return "Unverifiable", 0.0, None


async def run_verifier(draft_text: str, session_id: str, on_progress=None) -> List[VerificationChunk]:
    sentences = _split_into_sentences(draft_text)
    results = []

    if on_progress:
        on_progress(f"Verifying {len(sentences)} claim(s) from your draft...")

    for i, sentence in enumerate(sentences):
        if on_progress:
            on_progress(f"Checking claim {i+1}/{len(sentences)}: '{sentence[:60]}...'")
        similar_chunks = retrieve_similar(sentence, session_id, top_k=3)
        best_source = similar_chunks[0]["source_id"] if similar_chunks else None
        status, confidence, suggestion = _verify_sentence(sentence, similar_chunks)
        results.append(VerificationChunk(
            chunk=sentence, status=status, source_ref=best_source,
            confidence=confidence, suggestion=suggestion,
        ))

    if on_progress:
        verified = sum(1 for r in results if r.status == "Verified")
        on_progress(f"Verification complete. {verified}/{len(results)} claims verified.")
    return results


def calculate_integrity_score(verification_log: List[VerificationChunk]) -> float:
    if not verification_log:
        return 0.0
    verified = sum(1 for v in verification_log if v.status in ("Verified", "Partial"))
    return round((verified / len(verification_log)) * 100, 1)
