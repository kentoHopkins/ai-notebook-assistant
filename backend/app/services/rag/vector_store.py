import os
from functools import lru_cache
from pathlib import Path
import chromadb
from dotenv import load_dotenv
from backend.app.services.rag.embeddings import get_embedding_function

PROJECT_ROOT = Path(__file__).resolve().parents[4]
load_dotenv(PROJECT_ROOT / ".env")

def get_chroma_path() -> str:
    configured_path = os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        "./data/chroma",
    )
    path = Path(configured_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

@lru_cache(maxsize=1)
def get_chroma_client():
    return chromadb.PersistentClient(
        path=get_chroma_path()
    )

def get_collection(notebook_id: int):
    if notebook_id <= 0:
        raise ValueError("notebook_id must be greater than zero.")
    collection_name = f"notebook_{notebook_id}"
    return get_chroma_client().get_or_create_collection(
        name=collection_name,
        embedding_function=get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )

def add_document_chunks(
    notebook_id: int,
    document_id: int,
    filename: str,
    chunks: list[str],
) -> int:
    if notebook_id <= 0:
        raise ValueError("notebook_id must be greater than zero.")
    if document_id <= 0:
        raise ValueError("document_id must be greater than zero.")
    if not chunks:
        return 0
    collection = get_collection(notebook_id)
    batch_size = 16
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        ids = [
            f"doc_{document_id}_chunk_{index}"
            for index in range(start, start + len(batch))
        ]
        metadatas = [
            {
                "notebook_id": notebook_id,
                "document_id": document_id,
                "filename": filename,
                "chunk_index": index,
            }
            for index in range(start, start + len(batch))
        ]
        collection.upsert(
            ids=ids,
            documents=batch,
            metadatas=metadatas,
        )
    return len(chunks)

def search_chunks(
    notebook_id: int,
    query: str,
    n_results: int = 5,
) -> list[dict]:
    if notebook_id <= 0:
        raise ValueError("notebook_id must be greater than zero.")
    if not query or not query.strip():
        raise ValueError("query cannot be empty.")
    if n_results <= 0:
        raise ValueError("n_results must be greater than zero.")
    collection = get_collection(notebook_id)
    total_chunks = collection.count()
    if total_chunks == 0:
        return []
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, total_chunks),
        include=["documents", "metadatas", "distances"],
    )
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    return [
        {
            "text": document,
            "metadata": metadata,
            "distance": distance,
        }
        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        )
    ]

def delete_document_chunks(
    notebook_id: int,
    document_id: int,
) -> None:
    if notebook_id <= 0:
        raise ValueError("notebook_id must be greater than zero.")
    if document_id <= 0:
        raise ValueError("document_id must be greater than zero.")
    collection = get_collection(notebook_id)
    collection.delete(
        where={
            "document_id": document_id,
        }
    )