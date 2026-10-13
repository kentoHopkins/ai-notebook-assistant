import pytest
from backend.app.services.rag.chunker import chunk_text

def test_empty_text_returns_empty_list():
    assert chunk_text("") == []

def test_whitespace_returns_empty_list():
    assert chunk_text("   \n\t  ") == []

def test_short_text_returns_one_chunk():
    text = "Machine learning uses data."
    assert chunk_text(text) == [text]

def test_long_text_is_split_into_multiple_chunks():
    text = "A" * 2500
    chunks = chunk_text(
        text,
        chunk_size=1000,
        chunk_overlap=200,
    )
    assert len(chunks) == 3
    assert all(len(chunk) <= 1000 for chunk in chunks)

def test_chunks_have_expected_overlap():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 100
    chunks = chunk_text(
        text,
        chunk_size=1000,
        chunk_overlap=200,
    )
    assert len(chunks) > 1
    for i in range(len(chunks) - 1):
        assert chunks[i][-200:] == chunks[i + 1][:200]

def test_invalid_chunk_size_raises_error():
    with pytest.raises(ValueError):
        chunk_text("Example text", chunk_size=0)

def test_negative_overlap_raises_error():
    with pytest.raises(ValueError):
        chunk_text("Example text", chunk_overlap=-1)

def test_overlap_equal_to_chunk_size_raises_error():
    with pytest.raises(ValueError):
        chunk_text(
            "Example text",
            chunk_size=100,
            chunk_overlap=100,
        )