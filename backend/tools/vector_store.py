# backend/tools/vector_store.py
# Lightweight ChromaDB — no sentence-transformers (saves 400MB RAM)

import os
import logging
import chromadb
from typing import List
from backend.models import Source

logger = logging.getLogger("zora.vectorstore")
_client = None
_collections = {}

def _get_client():
    global _client
    if _client is None:
        db_path = os.getenv("CHROMA_DB_PATH", "./zora_chroma_db")
        os.makedirs(db_path, exist_ok=True)
        _client = chromadb.PersistentClient(path=db_path)
    return _client

def _get_collection(namespace: str):
    if namespace in _collections:
        return _collections[namespace]
    col = _get_client().get_or_create_collection(name=namespace, metadata={"hnsw:space": "cosine"})
    _collections[namespace] = col
    return col

def embed_sources(sources: List[Source], session_id: str):
    try:
        col = _get_collection(f"zora_{session_id[:8]}")
        docs, ids, metas = [], [], []
        for source in sources:
            words = source.summary.split()
            chunks = [" ".join(words[i:i+150]) for i in range(0, len(words), 150)]
            for j, chunk in enumerate(chunks):
                docs.append(chunk)
                ids.append(f"{source.id}_chunk{j}")
                metas.append({"source_id": source.id, "url": source.url, "title": source.title, "reliability": source.reliability_score})
        if docs:
            col.upsert(documents=docs, ids=ids, metadatas=metas)
            logger.info(f"Embedded {len(docs)} chunks")
    except Exception as e:
        logger.error(f"Embedding failed: {e}")

def retrieve_similar(query: str, session_id: str, top_k: int = 3) -> List[dict]:
    try:
        col = _get_collection(f"zora_{session_id[:8]}")
        count = col.count()
        if count == 0: return []
        results = col.query(query_texts=[query], n_results=min(top_k, count))
        return [{
            "content": doc,
            "source_id": results["metadatas"][0][i].get("source_id"),
            "url": results["metadatas"][0][i].get("url"),
            "title": results["metadatas"][0][i].get("title"),
            "similarity": round(1 - (results["distances"][0][i] if results.get("distances") else 0.5), 3),
        } for i, doc in enumerate(results["documents"][0])]
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return []

def cleanup_session(session_id: str):
    try:
        _get_client().delete_collection(f"zora_{session_id[:8]}")
        _collections.pop(f"zora_{session_id[:8]}", None)
    except Exception:
        pass