import pytest
from backend.app.services.rag import vector_store

class FakeEmbeddingFunction:
    def __call__(self, input):
        return [
            [
                float(len(text)),
                float(text.lower().count("python")),
                1.0,
            ]
            for text in input
        ]
    def embed_query(self, input):
        """Generate embeddings for search queries."""
        return self(input)
    def name(self):
        return "default"
    @staticmethod
    def build_from_config(config):
        return FakeEmbeddingFunction()
    def get_config(self):
        return {}
    @staticmethod
    def validate_config(config):
        return config

@pytest.fixture
def isolated_vector_store(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "CHROMA_PERSIST_DIRECTORY",
        str(tmp_path / "chroma"),
    )
    vector_store.get_chroma_client.cache_clear()
    monkeypatch.setattr(
        vector_store,
        "get_embedding_function",
        FakeEmbeddingFunction,
    )
    yield
    vector_store.get_chroma_client.cache_clear()

def test_add_and_search_chunks(isolated_vector_store):
    chunks = [
        "Python is a programming language.",
        "Machine learning uses training data.",
    ]
    stored_count = vector_store.add_document_chunks(
        notebook_id=1,
        document_id=10,
        filename="notes.txt",
        chunks=chunks,
    )
    assert stored_count == 2
    results = vector_store.search_chunks(
        notebook_id=1,
        query="Python programming",
        n_results=2,
    )
    assert len(results) == 2
    assert all("text" in result for result in results)
    assert all("metadata" in result for result in results)
    source_metadata = [
        result["metadata"]
        for result in results
    ]
    assert all(
        metadata["document_id"] == 10
        for metadata in source_metadata
    )
    assert all(
        metadata["notebook_id"] == 1
        for metadata in source_metadata
    )

def test_notebooks_are_isolated(isolated_vector_store):
    vector_store.add_document_chunks(
        notebook_id=1,
        document_id=10,
        filename="python.txt",
        chunks=["Python programming documentation."],
    )
    vector_store.add_document_chunks(
        notebook_id=2,
        document_id=20,
        filename="java.txt",
        chunks=["Java programming documentation."],
    )
    notebook_one_results = vector_store.search_chunks(
        notebook_id=1,
        query="programming documentation",
    )
    notebook_two_results = vector_store.search_chunks(
        notebook_id=2,
        query="programming documentation",
    )
    assert all(
        result["metadata"]["notebook_id"] == 1
        for result in notebook_one_results
    )
    assert all(
        result["metadata"]["notebook_id"] == 2
        for result in notebook_two_results
    )
    assert all(
        result["metadata"]["document_id"] != 20
        for result in notebook_one_results
    )

def test_delete_document_chunks(isolated_vector_store):
    vector_store.add_document_chunks(
        notebook_id=1,
        document_id=10,
        filename="notes.txt",
        chunks=[
            "First chunk.",
            "Second chunk.",
        ],
    )
    vector_store.delete_document_chunks(
        notebook_id=1,
        document_id=10,
    )
    results = vector_store.search_chunks(
        notebook_id=1,
        query="First chunk",
    )
    assert results == []

def test_empty_chunks_are_not_stored(isolated_vector_store):
    stored_count = vector_store.add_document_chunks(
        notebook_id=1,
        document_id=10,
        filename="empty.txt",
        chunks=[],
    )
    assert stored_count == 0

def test_invalid_notebook_id_raises_error(isolated_vector_store):
    with pytest.raises(ValueError):
        vector_store.get_collection(notebook_id=0)

def test_empty_query_raises_error(isolated_vector_store):
    with pytest.raises(ValueError):
        vector_store.search_chunks(
            notebook_id=1,
            query="   ",
        )