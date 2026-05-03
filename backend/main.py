# backend/main.py
# FastAPI server — REST + WebSocket for real-time progress streaming

import os
import json
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("vera.api")

from backend.models import ResearchRequest, ZoraSession
from backend.agents.orchestrator import run_zora_pipeline

app = FastAPI(title="Zora: The Integrity Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output dirs exist
os.makedirs("./output/receipts", exist_ok=True)

# Serve receipt files
receipts_dir = Path("./output/receipts")
if receipts_dir.exists():
    app.mount("/receipts", StaticFiles(directory=str(receipts_dir)), name="receipts")

# Serve frontend static files (if built)
frontend_dist = Path("./frontend/dist")
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")


@app.get("/")
async def root():
    # Serve frontend if built
    index_path = frontend_dist / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Vera API is running. See /docs for API reference."}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/research", response_model=dict)
async def research_endpoint(request: ResearchRequest):
    """
    Synchronous research endpoint (no streaming).
    Returns complete session result.
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

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


@app.websocket("/ws/research")
async def research_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time progress streaming.
    Client sends: {"topic": "...", "draft_text": "...", "user_id": "..."}
    Server streams: progress updates + final result
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)
        request = ResearchRequest(**request_data)

        async def send_progress(update):
            await websocket.send_json({
                "type": "progress",
                "session_id": update.session_id,
                "state": update.state,
                "message": update.message,
                "data": update.data,
            })

        # Run pipeline with live progress
        session = await run_zora_pipeline(request, on_progress=send_progress)

        # Send final result
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

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client")
    except json.JSONDecodeError:
        await websocket.send_json({"type": "error", "message": "Invalid JSON payload"})
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
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
    uvicorn.run(
        "backend.main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=os.getenv("DEBUG", "true").lower() == "true",
    )
