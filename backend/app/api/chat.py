from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.notebook import Notebook
from backend.app.models.chat_message import ChatMessage
from backend.app.schemas.chat import (
    QuestionRequest,
    QuestionResponse,
    SourceCitation,
)
from backend.app.schemas.chat_message import ChatMessageResponse
from backend.app.services.groq_service import (
    generate_answer,
    rewrite_question,
)
import os
from dotenv import load_dotenv
from backend.app.services.rag.vector_store import (
    search_chunks,
    search_chunks_bm25,
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../..")
)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

router = APIRouter(tags=["Chat"])

@router.post(
    "/notebooks/{notebook_id}/ask",
    response_model=QuestionResponse,
)
def ask_question(
    notebook_id: int,
    request: QuestionRequest,
    db: Session = Depends(get_db),
):
    notebook = db.get(Notebook, notebook_id)
    if notebook is None:
        raise HTTPException(
            status_code=404,
            detail="Notebook not found.",
        )
    history_statement = (
        select(ChatMessage)
        .where(ChatMessage.notebook_id == notebook_id)
        .order_by(
            ChatMessage.created_at.desc(),
            ChatMessage.id.desc(),
        )
        .limit(10)
    )
    history_records = db.scalars(history_statement).all()
    conversation_history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in reversed(history_records)
    ]
    try:
        search_query = rewrite_question(
            question=request.question,
            conversation_history=conversation_history,
        )
    except Exception:
        search_query = request.question
    try:
        retrieval_mode = os.getenv(
            "RETRIEVAL_MODE",
            "vector",
        ).strip().lower()

        if retrieval_mode == "vector":
            retrieved_chunks = search_chunks(
                notebook_id=notebook_id,
                query=search_query,
                n_results=5,
            )
        elif retrieval_mode == "bm25":
            retrieved_chunks = search_chunks_bm25(
                notebook_id=notebook_id,
                query=search_query,
                n_results=5,
            )
        else:
            raise ValueError(
                f"Unsupported RETRIEVAL_MODE: {retrieval_mode}"
            )

        print("\n--- Retrieved Chunks ---")
        for chunk in retrieved_chunks:
            print(
                "Filename:",
                chunk["metadata"].get("filename"),
            )
            print("Chunk:", chunk["text"])
            print("Distance:", chunk["distance"])
            print("------------------------")
        print("Original question:", request.question)
        print("Search query:", search_query)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve document context.",
        ) from exc
    try:
        answer = generate_answer(
            question=request.question,
            context_chunks=retrieved_chunks,
            conversation_history=conversation_history,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to generate an answer using the AI service.",
        ) from exc
    sources = []
    seen_sources = set()
    for chunk in retrieved_chunks:
        metadata = chunk["metadata"]
        source_key = (
            metadata["document_id"],
            metadata["chunk_index"],
        )
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)
        sources.append(
            SourceCitation(
                document_id=metadata["document_id"],
                filename=metadata["filename"],
                chunk_index=metadata["chunk_index"],
            )
        )
    user_message = ChatMessage(
        notebook_id=notebook_id,
        role="user",
        content=request.question,
    )
    assistant_message = ChatMessage(
        notebook_id=notebook_id,
        role="assistant",
        content=answer,
    )
    try:
        db.add_all(
            [
                user_message,
                assistant_message,
            ]
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save conversation history.",
        ) from exc
    return QuestionResponse(
        notebook_id=notebook_id,
        question=request.question,
        answer=answer,
        sources=sources,
    )

@router.get(
    "/notebooks/{notebook_id}/messages",
    response_model=list[ChatMessageResponse],
)
def get_chat_history(
    notebook_id: int,
    db: Session = Depends(get_db),
):
    notebook = db.get(Notebook, notebook_id)
    if notebook is None:
        raise HTTPException(
            status_code=404,
            detail="Notebook not found.",
        )
    statement = (
        select(ChatMessage)
        .where(ChatMessage.notebook_id == notebook_id)
        .order_by(
            ChatMessage.created_at,
            ChatMessage.id,
        )
    )
    messages = db.scalars(statement).all()
    return messages