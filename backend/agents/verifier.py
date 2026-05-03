# backend/agents/verifier.py
# The Verifier Agent — anti-hallucination engine (Gemini version)

import re
import logging
from typing import List, Callable, Optional

from backend.models import VerificationChunk
from backend.tools.vector_store import retrieve_similar
from backend.utils.gemini_client import generate_json

logger = logging.getLogger("vera.verifier")


def _split_into_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    merged = []
    buffer = ""
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


def _verify_sentence_with_gemini(sentence: str, context_chunks: List[dict]) -> tuple:
    if not context_chunks:
        return "Unverifiable", 0.0, "No sources found for this claim."

    source_context = "\n\n".join(
        f"[Source {c['source_id']}] ({c['title']}): {c['content']}"
        for c in context_chunks
    )

    prompt = f"""You are a strict academic fact-checker.

STUDENT'S CLAIM:
"{sentence}"

AVAILABLE SOURCES:
{source_context}

Does any source EXPLICITLY or IMPLICITLY support the student's claim?

Respond with a JSON object ONLY (no markdown, no explanation):
{{"verdict": "TRUE or PARTIAL or FALSE", "confidence": 0.0 to 1.0, "suggestion": "correction string or null"}}

- TRUE = directly supported
- PARTIAL = related but not exact; provide a correction
- FALSE = contradicts or absent from sources"""

    try:
        result = generate_json(prompt, model_name="gemini-1.5-flash")
        verdict = str(result.get("verdict", "FALSE")).upper()
        confidence = float(result.get("confidence", 0.5))
        suggestion = result.get("suggestion")
        if suggestion in ("null", "", None):
            suggestion = None
        status_map = {"TRUE": "Verified", "PARTIAL": "Partial", "FALSE": "Hallucinated"}
        status = status_map.get(verdict, "Unverifiable")
        return status, confidence, suggestion
    except Exception as e:
        logger.error(f"Gemini verification failed: {e}")
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
        status, confidence, suggestion = _verify_sentence_with_gemini(sentence, similar_chunks)
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
