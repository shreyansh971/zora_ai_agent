# backend/agents/citation_specialist.py
# Citation Specialist — generates APA citations + final draft (Gemini version)

import logging
from typing import List, Optional
from backend.models import Source, VerificationChunk
from backend.utils.gemini_client import generate

logger = logging.getLogger("vera.citation")


def generate_apa_citation(source: Source) -> str:
    author = source.author if source.author and source.author != "Unknown" else "Unknown Author"
    year = source.date if source.date and source.date != "Unknown" else "n.d."
    return f"{author}. ({year}). {source.title}. Retrieved from {source.url}"


def generate_bibliography(sources: List[Source]) -> List[str]:
    return [generate_apa_citation(s) for s in sources]


async def generate_final_draft(
    topic: str,
    sources: List[Source],
    draft_text: Optional[str],
    verification_log: List[VerificationChunk],
    on_progress=None,
) -> str:
    if on_progress:
        on_progress("Compiling final grounded research draft with Gemini...")

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

Return ONLY the improved draft text, no preamble."""
    else:
        prompt = f"""Write a well-structured academic summary on: "{topic}"

Use ONLY the following verified sources. Cite them inline as [S1], [S2], etc.:

{source_summaries}

Requirements:
- 3-4 paragraphs
- Every claim must reference a source
- Formal academic tone
- End with a brief conclusion

Return ONLY the essay text, no preamble."""

    try:
        return generate(prompt, model_name="gemini-1.5-pro", temperature=0.3)
    except Exception as e:
        logger.error(f"Draft generation failed: {e}")
        # Fallback to flash model
        try:
            return generate(prompt, model_name="gemini-1.5-flash", temperature=0.3)
        except Exception as e2:
            logger.error(f"Flash fallback also failed: {e2}")
            return draft_text or "Draft generation failed. Please check your GEMINI_API_KEY."
