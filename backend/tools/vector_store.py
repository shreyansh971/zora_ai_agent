# backend/tools/vector_store.py
# ChromaDB vector memory for storing and retrieving research chunks

import os
import logging
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Optional
from backend.models import Source

logger = logging.getLogger("vera.vectorstore")

_client: Optional[chromadb.Client] = None
_collection = None


def _get_collection(namespace: str = "zora_research"):
    global _client, _collection
    if _client is None:
        db_path = os.getenv("CHROMA_DB_PATH", "./zora_chroma_db")
        os.makedirs(db_path, exist_ok=True)
        _client = chromadb.PersistentClient(path=db_path)

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    try:
        collection = _client.get_or_create_collection(
            name=namespace,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
        return collection
    except Exception as e:
        logger.error(f"ChromaDB collection error: {e}")
        raise


def embed_sources(sources: List[Source], session_id: str):
    """Embed all source summaries into the vector store."""
    collection = _get_collection(f"zora_{session_id[:8]}")
    docs, ids, metas = [], [], []

    for source in sources:
        # Chunk the summary into ~150 word pieces
        words = source.summary.split()
        chunks = [" ".join(words[i:i+150]) for i in range(0, len(words), 150)]
        for j, chunk in enumerate(chunks):
            chunk_id = f"{source.id}_chunk{j}"
            docs.append(chunk)
            ids.append(chunk_id)
            metas.append({
                "source_id": source.id,
                "url": source.url,
                "title": source.title,
                "reliability": source.reliability_score,
            })

    if docs:
        collection.upsert(documents=docs, ids=ids, metadatas=metas)
        logger.info(f"Embedded {len(docs)} chunks for session {session_id[:8]}")


def retrieve_similar(query: str, session_id: str, top_k: int = 3) -> List[dict]:
    """Retrieve top-K similar chunks from the vector store."""
    try:
        collection = _get_collection(f"zora_{session_id[:8]}")
        results = collection.query(
            query_texts=[query],
            n_results=min(top_k, collection.count()),
        )
        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            distance = results["distances"][0][i] if results.get("distances") else 0.5
            chunks.append({
                "content": doc,
                "source_id": meta.get("source_id"),
                "url": meta.get("url"),
                "title": meta.get("title"),
                "similarity": round(1 - distance, 3),
            })
        return chunks
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return []


def cleanup_session(session_id: str):
    """Remove the session's collection after use."""
    try:
        if _client:
            _client.delete_collection(f"zora_{session_id[:8]}")
    except Exception:
        pass
