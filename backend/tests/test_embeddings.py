from backend.app.services.rag.embeddings import (
    EMBEDDING_MODEL,
    get_embedding_function,
)

def test_embedding_model_name():
    assert EMBEDDING_MODEL == "all-MiniLM-L6-v2"

def test_get_embedding_function():
    embedding_fn = get_embedding_function()
    assert embedding_fn is not None
    assert callable(embedding_fn)