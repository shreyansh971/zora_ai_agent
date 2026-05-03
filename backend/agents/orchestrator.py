# backend/agents/orchestrator.py
# The Orchestrator Agent — Finite State Machine that drives the entire pipeline

import asyncio
import logging
from typing import Callable, Optional
from datetime import datetime

from backend.models import (
    ZoraSession, SessionMetadata, ResearchTrail,
    ResearchRequest, ProgressUpdate
)
from backend.agents.researcher import run_researcher
from backend.agents.verifier import run_verifier, calculate_integrity_score
from backend.agents.citation_specialist import generate_final_draft, generate_bibliography
from backend.tools.vector_store import embed_sources, cleanup_session
from backend.tools.pdf_generator import generate_receipt_pdf

logger = logging.getLogger("vera.orchestrator")

# FSM States
IDLE = "IDLE"
RESEARCHING = "RESEARCHING"
EMBEDDING = "EMBEDDING"
VERIFYING = "VERIFYING"
DRAFTING = "DRAFTING"
REPORTING = "REPORTING"
COMPLETE = "COMPLETE"
ERROR = "ERROR"


async def run_zora_pipeline(
    request: ResearchRequest,
    on_progress: Optional[Callable[[ProgressUpdate], None]] = None,
) -> ZoraSession:
    """
    Main Zora pipeline orchestrated as a Finite State Machine.
    Calls on_progress(ProgressUpdate) at each step for real-time UI updates.
    """
    # --- Initialize session ---
    session = ZoraSession(
        metadata=SessionMetadata(
            user_id=request.user_id,
            timestamp=datetime.utcnow().isoformat(),
            topic=request.topic,
        )
    )

    def progress(state: str, message: str, data: dict = None):
        session.state = state
        update = ProgressUpdate(
            session_id=session.session_id,
            state=state,
            message=message,
            data=data or {},
        )
        logger.info(f"[{state}] {message}")
        if on_progress:
            on_progress(update)

    def researcher_progress(msg: str):
        progress(RESEARCHING, msg)

    def verifier_progress(msg: str):
        progress(VERIFYING, msg)

    try:
        # Log the user's initial submission
        session.interaction_log.append({
            "role": "user",
            "content": f"Topic: {request.topic}" + (f" | Draft: {request.draft_text[:100]}..." if request.draft_text else ""),
        })

        # =========================================
        # STATE: RESEARCHING
        # =========================================
        progress(RESEARCHING, f"Starting research on: '{request.topic}'")

        # Handle too-broad topics
        word_count = len(request.topic.split())
        if word_count < 3:
            progress(RESEARCHING, f"Topic is broad — expanding search scope.")

        sources = await run_researcher(
            topic=request.topic,
            on_progress=researcher_progress,
        )

        if not sources:
            progress(ERROR, "No sources found. Try a more specific topic.")
            session.state = ERROR
            return session

        session.research_trail.sources = sources
        session.research_trail.queries = [
            f"{request.topic} research study",
            f"{request.topic} academic review",
            f"{request.topic} evidence analysis",
            f"{request.topic} scholarly findings",
        ]

        session.interaction_log.append({
            "role": "vera",
            "content": f"Found {len(sources)} sources: {', '.join(s.title[:30] for s in sources[:3])}",
        })

        # =========================================
        # STATE: EMBEDDING
        # =========================================
        progress(EMBEDDING, f"Embedding {len(sources)} sources into vector memory...")
        embed_sources(sources, session.session_id)
        progress(EMBEDDING, "Vector embeddings complete.")

        # =========================================
        # STATE: VERIFYING (only if draft provided)
        # =========================================
        if request.draft_text and request.draft_text.strip():
            progress(VERIFYING, "Draft detected — running anti-hallucination verification...")

            verification_log = await run_verifier(
                draft_text=request.draft_text,
                session_id=session.session_id,
                on_progress=verifier_progress,
            )
            session.research_trail.verification_log = verification_log
            session.integrity_score = calculate_integrity_score(verification_log)

            session.interaction_log.append({
                "role": "vera",
                "content": f"Verification complete. Integrity score: {session.integrity_score}%",
            })
        else:
            # No draft — co-pilot mode
            progress(VERIFYING, "No draft provided — switching to Co-Pilot mode. Will generate a grounded draft.")
            session.integrity_score = 100.0

        # =========================================
        # STATE: DRAFTING
        # =========================================
        progress(DRAFTING, "Generating final grounded draft with citations...")

        final_text = await generate_final_draft(
            topic=request.topic,
            sources=sources,
            draft_text=request.draft_text,
            verification_log=session.research_trail.verification_log,
            on_progress=lambda msg: progress(DRAFTING, msg),
        )

        session.outputs["final_text"] = final_text

        session.interaction_log.append({
            "role": "vera",
            "content": f"Final draft generated ({len(final_text.split())} words).",
        })

        # =========================================
        # STATE: REPORTING
        # =========================================
        progress(REPORTING, "Generating Research Receipt PDF...")

        bibliography = generate_bibliography(sources)
        session.outputs["bibliography"] = bibliography

        try:
            pdf_path = generate_receipt_pdf(session, bibliography)
            session.outputs["receipt_path"] = pdf_path
            session.outputs["receipt_url"] = f"/receipts/{pdf_path.split('/')[-1]}"
            session.interaction_log.append({
                "role": "vera",
                "content": f"Research Receipt generated: {pdf_path.split('/')[-1]}",
            })
            progress(REPORTING, f"Receipt saved: {pdf_path.split('/')[-1]}")
        except Exception as e:
            logger.warning(f"PDF generation failed: {e}")
            session.outputs["receipt_url"] = None

        # =========================================
        # STATE: COMPLETE
        # =========================================
        session.state = COMPLETE
        progress(COMPLETE, "✅ Zora pipeline complete!", {
            "integrity_score": session.integrity_score,
            "sources_count": len(sources),
            "claims_verified": sum(1 for v in session.research_trail.verification_log if v.status == "Verified"),
        })

    except Exception as e:
        logger.exception(f"Pipeline error: {e}")
        progress(ERROR, f"Pipeline error: {str(e)}")
        session.state = ERROR

    finally:
        # Cleanup temporary vector namespace
        try:
            cleanup_session(session.session_id)
        except Exception:
            pass

    return session
