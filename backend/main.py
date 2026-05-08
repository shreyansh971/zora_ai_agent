# backend/main.py — Zora: The Integrity Agent
# REST API (no WebSocket dependency for free hosting compatibility)

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("zora.api")

from backend.models import ResearchRequest, ZoraSession
from backend.agents.orchestrator import run_zora_pipeline

app = FastAPI(title="Zora: The Integrity Agent", version="1.0.0")

# Allow all origins (Vercel, localhost, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("./output/receipts", exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Zora API is running", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/research")
async def research_endpoint(request: ResearchRequest):
    """Main research endpoint — runs the full Zora pipeline."""
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    logger.info(f"Research request: {request.topic[:80]}")

    session = await run_zora_pipeline(request)

    return {
        "session_id": session.session_id,
        "state": session.state,
        "integrity_score": session.integrity_score,
        "sources": [s.dict() for s in session.research_trail.sources],
        "verification_log": [v.dict() for v in session.research_trail.verification_log],
        "final_text": session.outputs.get("final_text", ""),
        "bibliography": session.outputs.get("bibliography", []),
        "receipt_url": session.outputs.get("receipt_url"),
        "interaction_log": session.interaction_log,
        "queries": session.research_trail.queries,
    }


# Keep WebSocket endpoint for local dev
@app.websocket("/ws/research")
async def research_websocket(websocket):
    from fastapi import WebSocket
    from fastapi.websockets import WebSocketDisconnect
    import json
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        request = ResearchRequest(**json.loads(data))

        async def send_progress(update):
            await websocket.send_json({
                "type": "progress",
                "session_id": update.session_id,
                "state": update.state,
                "message": update.message,
                "data": update.data,
            })

        session = await run_zora_pipeline(request, on_progress=send_progress)
        await websocket.send_json({
            "type": "complete",
            "session_id": session.session_id,
            "state": session.state,
            "integrity_score": session.integrity_score,
            "sources": [s.dict() for s in session.research_trail.sources],
            "verification_log": [v.dict() for v in session.research_trail.verification_log],
            "final_text": session.outputs.get("final_text", ""),
            "bibliography": session.outputs.get("bibliography", []),
            "receipt_url": session.outputs.get("receipt_url"),
            "interaction_log": session.interaction_log,
            "queries": session.research_trail.queries,
        })
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0",
                port=int(os.getenv("PORT", 8000)),
                reload=os.getenv("DEBUG", "true").lower() == "true")