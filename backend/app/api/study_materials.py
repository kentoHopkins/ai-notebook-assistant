from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.notebook import Notebook
from backend.app.models.document import Document
from backend.app.schemas.study_material import (
    SummaryResponse,
    StudyGuideResponse,
)
from backend.app.services.study_material_service import (
    generate_summary,
    generate_study_guide,
)
from backend.app.schemas.study_material import QuizRequest, QuizResponse
from backend.app.services.study_material_service import generate_quiz

router = APIRouter(tags=["Study Materials"])

@router.post(
    "/notebooks/{notebook_id}/summary",
    response_model=SummaryResponse,
)
def create_summary(
    notebook_id: int,
    db: Session = Depends(get_db),
):
    notebook = db.scalar(
        select(Notebook).where(Notebook.id == notebook_id)
    )
    if notebook is None:
        raise HTTPException(
            status_code=404,
            detail="Notebook not found.",
        )
    documents = db.scalars(
        select(Document)
        .where(Document.notebook_id == notebook_id)
        .order_by(Document.id)
    ).all()
    if not documents:
        raise HTTPException(
            status_code=400,
            detail="This notebook has no documents to summarize.",
        )
    document_contents = [
        document.content
        for document in documents
        if document.content and document.content.strip()
    ]
    if not document_contents:
        raise HTTPException(
            status_code=400,
            detail="No readable document content is available.",
        )
    try:
        summary = generate_summary(document_contents)
    except Exception as exc:
        print(f"Summary generation failed: {exc}")

        raise HTTPException(
            status_code=502,
            detail="Failed to generate a summary. Please try again.",
        ) from exc
    return SummaryResponse(
        notebook_id=notebook_id,
        summary=summary,
        source_count=len(document_contents),
    )

@router.post(
    "/notebooks/{notebook_id}/study-guide",
    response_model=StudyGuideResponse,
)
def create_study_guide(
    notebook_id: int,
    db: Session = Depends(get_db),
):
    notebook = db.scalar(
        select(Notebook).where(Notebook.id == notebook_id)
    )
    if notebook is None:
        raise HTTPException(
            status_code=404,
            detail="Notebook not found.",
        )
    documents = db.scalars(
        select(Document)
        .where(Document.notebook_id == notebook_id)
        .order_by(Document.id)
    ).all()
    if not documents:
        raise HTTPException(
            status_code=400,
            detail="This notebook has no documents to create a study guide from.",
        )
    document_contents = [
        document.content
        for document in documents
        if document.content and document.content.strip()
    ]
    if not document_contents:
        raise HTTPException(
            status_code=400,
            detail="No readable document content is available.",
        )
    try:
        study_guide = generate_study_guide(document_contents)
    except Exception as exc:
        print(f"Study-guide generation failed: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Failed to generate a study guide. Please try again.",
        ) from exc
    return StudyGuideResponse(
        notebook_id=notebook_id,
        study_guide=study_guide,
        source_count=len(document_contents),
    )

@router.post(
    "/notebooks/{notebook_id}/quiz",
    response_model=QuizResponse,
)
def create_quiz(
    notebook_id: int,
    request: QuizRequest = QuizRequest(),
    db: Session = Depends(get_db),
):
    notebook = db.get(Notebook, notebook_id)
    if notebook is None:
        raise HTTPException(
            status_code=404,
            detail="Notebook not found.",
        )
    documents = db.scalars(
        select(Document)
        .where(Document.notebook_id == notebook_id)
        .order_by(Document.id)
    ).all()
    if not documents:
        raise HTTPException(
            status_code=400,
            detail="This notebook does not contain any documents.",
        )
    document_contents = [
        document.content.strip()
        for document in documents
        if document.content and document.content.strip()
    ]
    if not document_contents:
        raise HTTPException(
            status_code=400,
            detail="No readable document content is available.",
        )
    try:
        quiz = generate_quiz(
            document_contents,
            num_questions=request.num_questions,
        )
        return QuizResponse(
            notebook_id=notebook_id,
            quiz=quiz,
            source_count=len(document_contents),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Quiz generation failed: {exc}",
        ) from exc
    except Exception as exc:
        print(f"Quiz generation error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Unable to generate a quiz. Please try again.",
        ) from exc