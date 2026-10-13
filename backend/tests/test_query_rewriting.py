from unittest.mock import MagicMock
from backend.app.services import groq_service

def test_rewrite_question_without_history():
    result = groq_service.rewrite_question(
        question="What is ChromaDB?",
        conversation_history=None,
    )
    assert result == "What is ChromaDB?"

def test_rewrite_question_with_history(monkeypatch):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        "What are the advantages of ChromaDB?"
    )
    mock_client.chat.completions.create.return_value = mock_response
    monkeypatch.setattr(
        groq_service,
        "get_groq_client",
        lambda: mock_client,
    )
    history = [
        {
            "role": "user",
            "content": "What is ChromaDB used for?",
        },
        {
            "role": "assistant",
            "content": (
                "ChromaDB is a vector database that stores embeddings."
            ),
        },
    ]
    result = groq_service.rewrite_question(
        question="What are its advantages?",
        conversation_history=history,
    )
    assert result == "What are the advantages of ChromaDB?"
    mock_client.chat.completions.create.assert_called_once()