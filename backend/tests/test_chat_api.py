from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.api.chat import ask_question
from backend.app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.database import Base
from backend.app.models.notebook import Notebook
from backend.app.models.document import Document


client = TestClient(app)

def test_ask_question_returns_answer_and_sources(monkeypatch):
    def fake_search_chunks(notebook_id, query, n_results):
        return [
            {
                "text": "Marine biology studies ocean organisms.",
                "metadata": {
                    "notebook_id": notebook_id,
                    "document_id": 10,
                    "filename": "marine_biology.txt",
                    "chunk_index": 0,
                },
                "distance": 0.2,
            }
        ]
    def fake_generate_answer(
        question,
        context_chunks,
        conversation_history=None,
    ):
        return "Marine biology studies organisms living in marine environments."
    monkeypatch.setattr(
        "backend.app.api.chat.search_chunks",
        fake_search_chunks,
    )
    monkeypatch.setattr(
        "backend.app.api.chat.generate_answer",
        fake_generate_answer,
    )
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as db:
        notebook = Notebook(
            title="Marine Biology",
            description="Marine biology test notebook",
        )
        db.add(notebook)
        db.commit()
        db.refresh(notebook)
        notebook_id = notebook.id
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.post(
            f"/notebooks/{notebook_id}/ask",
            json={"question": "What is marine biology?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notebook_id"] == notebook_id
        assert data["question"] == "What is marine biology?"
        assert "marine environments" in data["answer"]
        assert len(data["sources"]) == 1
        assert data["sources"][0]["filename"] == "marine_biology.txt"
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()

def test_ask_question_rejects_empty_question():
    response = client.post(
        "/notebooks/1/ask",
        json={"question": ""},
    )
    assert response.status_code == 422

def test_ask_question_notebook_not_found():
    response = client.post(
        "/notebooks/999999/ask",
        json={"question": "What is marine biology?"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Notebook not found."

def test_ask_question_groq_failure(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as db:
        notebook = Notebook(
            title="Test Notebook",
            description="Testing AI failure",
        )
        db.add(notebook)
        db.commit()
        db.refresh(notebook)
        notebook_id = notebook.id
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    def fake_search_chunks(notebook_id, query, n_results):
        return [
            {
                "text": "Marine biology studies ocean organisms.",
                "metadata": {
                    "notebook_id": notebook_id,
                    "document_id": 10,
                    "filename": "marine_biology.txt",
                    "chunk_index": 0,
                },
                "distance": 0.2,
            }
        ]
    def fake_generate_answer(question, context_chunks):
        raise RuntimeError("Simulated Groq failure")
    monkeypatch.setattr(
        "backend.app.api.chat.search_chunks",
        fake_search_chunks,
    )
    monkeypatch.setattr(
        "backend.app.api.chat.generate_answer",
        fake_generate_answer,
    )
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.post(
            f"/notebooks/{notebook_id}/ask",
            json={"question": "What is marine biology?"},
        )
        assert response.status_code == 502
        assert response.json()["detail"] == (
            "Failed to generate an answer using the AI service."
        )

    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()

def test_ask_question_retrieves_from_requested_notebook(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )
    Base.metadata.create_all(bind=test_engine)
    with TestingSessionLocal() as db:
        notebook = Notebook(
            title="Isolation Test",
            description="Testing notebook isolation",
        )
        db.add(notebook)
        db.commit()
        db.refresh(notebook)
        notebook_id = notebook.id
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    retrieved_notebook_ids = []
    def fake_search_chunks(notebook_id, query, n_results):
        retrieved_notebook_ids.append(notebook_id)
        return [
            {
                "text": "Test content for the requested notebook.",
                "metadata": {
                    "notebook_id": notebook_id,
                    "document_id": 20,
                    "filename": "test.txt",
                    "chunk_index": 0,
                },
                "distance": 0.1,
            }
        ]
    def fake_generate_answer(
        question,
        context_chunks,
        conversation_history=None,
    ):
        return "Test answer."
    monkeypatch.setattr(
        "backend.app.api.chat.search_chunks",
        fake_search_chunks,
    )
    monkeypatch.setattr(
        "backend.app.api.chat.generate_answer",
        fake_generate_answer,
    )
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.post(
            f"/notebooks/{notebook_id}/ask",
            json={"question": "What is in this notebook?"},
        )
        assert response.status_code == 200
        assert retrieved_notebook_ids == [notebook_id]
        assert response.json()["sources"][0]["filename"] == "test.txt"
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()