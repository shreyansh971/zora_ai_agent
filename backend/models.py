# backend/models.py
# Core Pydantic models for Vera's data schema

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid


class Source(BaseModel):
    id: str
    url: str
    title: str
    author: Optional[str] = "Unknown"
    date: Optional[str] = "Unknown"
    content_hash: str
    summary: str
    reliability_score: float = 0.0


class VerificationChunk(BaseModel):
    chunk: str
    status: Literal["Verified", "Hallucinated", "Partial", "Unverifiable"]
    source_ref: Optional[str] = None
    confidence: float = 0.0
    suggestion: Optional[str] = None


class ResearchTrail(BaseModel):
    queries: List[str] = []
    sources: List[Source] = []
    verification_log: List[VerificationChunk] = []


class SessionMetadata(BaseModel):
    user_id: str
    timestamp: str
    topic: str


class ZoraSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: SessionMetadata
    research_trail: ResearchTrail = Field(default_factory=ResearchTrail)
    outputs: dict = Field(default_factory=dict)
    state: str = "IDLE"
    interaction_log: List[dict] = []
    integrity_score: Optional[float] = None


class ResearchRequest(BaseModel):
    user_id: str = "anonymous"
    topic: str
    draft_text: Optional[str] = None


class ProgressUpdate(BaseModel):
    session_id: str
    state: str
    message: str
    data: Optional[dict] = None
