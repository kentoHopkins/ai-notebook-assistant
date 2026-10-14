from pathlib import Path
import tempfile
import requests
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.document import Document
from backend.app.models.notebook import Notebook
from backend.app.schemas.document import DocumentResponse, DocumentURLCreate
from backend.app.services.document_loader import (
    extract_pdf,
    extract_pptx,
    extract_txt,
    extract_webpage,
)
from backend.app.services.rag.chunker import chunk_text
from backend.app.services.rag.vector_store import add_document_chunks, delete_document_chunks

router = APIRouter(
    prefix="/notebooks/{notebook_id}/documents",
    tags=["Documents"],
)

@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    notebook_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a document to a notebook and extract its text.
    """
    #verify that the destination notebook exists
    notebook = db.query(Notebook).filter(
        Notebook.id == notebook_id
    ).first()
    if notebook is None:
        raise HTTPException(
            status_code=404,
            detail="Notebook not found.",
        )
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()
    extractors = {
        ".txt": ("txt", extract_txt),
        ".pdf": ("pdf", extract_pdf),
        ".pptx": ("pptx", extract_pptx),
    }
    if extension not in extractors:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload a TXT, PDF, or PPTX file.",
        )
    source_type, extractor = extractors[extension]
    max_file_size = 10 * 1024 * 1024  # 10 MB
    file_bytes = await file.read(max_file_size + 1)

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(file_bytes) > max_file_size:
        raise HTTPException(
            status_code=413,
            detail="The uploaded file exceeds the 10 MB limit.",
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_path = Path(temp_file.name)
        content = extractor(temp_path)

    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to extract document text: {exc}",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file could not be processed. Check that it is a valid document.",
        ) from exc

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        await file.close()

    document = Document(
        notebook_id=notebook_id,
        filename=filename,
        source_type=source_type,
        source_url=None,
        content=content,
    )
    try:
        db.add(document)
        db.flush()
        chunks = chunk_text(content)
        print(f"[URL DEBUG] Chunking succeeded: {len(chunks)} chunks", flush=True)
        print("[URL DEBUG] Starting ChromaDB storage and embedding", flush=True)
        add_document_chunks(
            notebook_id=notebook_id,
            document_id=document.id,
            filename=filename,
            chunks=chunks,
        )
        print("[URL DEBUG] ChromaDB storage completed", flush=True)
        db.commit()
        db.refresh(document)
    except Exception as exc:
        db.rollback()
        if document.id is not None:
            try:
                delete_document_chunks(
                    notebook_id=notebook_id,
                    document_id=document.id,
                )
            except Exception:
                pass
        raise HTTPException(
            status_code=500,
            detail="Failed to process and store the document.",
        ) from exc
    return document

@router.post("/url", response_model=DocumentResponse, status_code=201)
def add_document_from_url(
    notebook_id: int,
    request: DocumentURLCreate,
    db: Session = Depends(get_db),
):
    """Import a public webpage into a notebook."""

    #check notebook exist
    notebook = db.query(Notebook).filter(
        Notebook.id == notebook_id
    ).first()
    if notebook is None:
        raise HTTPException(
            status_code=404,
            detail="Notebook not found.",
        )
    
    url = str(request.url)
    try:
        content = extract_webpage(url)
        print(f"[URL DEBUG] Extraction succeeded: {len(content)} characters", flush=True)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve the webpage.",
        ) from exc

    #construct a filename from the URL hostname
    parsed_url = urlparse(url)
    filename = f"{parsed_url.hostname or 'webpage'}.txt"
    document = Document(
        notebook_id=notebook_id,
        filename=filename,
        source_type="url",
        source_url=url,
        content=content,
    )
    try:
        db.add(document)
        db.flush()
        chunks = chunk_text(content)
        print(f"[URL DEBUG] Chunking succeeded: {len(chunks)} chunks", flush=True)
        print("[URL DEBUG] Starting ChromaDB storage and embedding", flush=True)
        add_document_chunks(
            notebook_id=notebook_id,
            document_id=document.id,
            filename=filename,
            chunks=chunks,
        )
        print("[URL DEBUG] ChromaDB storage completed", flush=True)
        db.commit()
        db.refresh(document)
    except Exception as exc:
        db.rollback()
        if document.id is not None:
            try:
                delete_document_chunks(
                    notebook_id=notebook_id,
                    document_id=document.id,
                )
            except Exception:
                pass
        raise HTTPException(
            status_code=500,
            detail="Failed to process and store the document.",
        ) from exc
    return document

@router.get("", response_model=list[DocumentResponse])
def list_documents(
    notebook_id: int,
    db: Session = Depends(get_db),
):
    """Return all documents belonging to a notebook."""
    notebook = db.query(Notebook).filter(
        Notebook.id == notebook_id
    ).first()
    if notebook is None:
        raise HTTPException(
            status_code=404,
            detail="Notebook not found.",
        )
    documents = (
        db.query(Document)
        .filter(Document.notebook_id == notebook_id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return documents

@router.delete("/{document_id}", status_code=204)
def delete_document(
    notebook_id: int,
    document_id: int,
    db: Session = Depends(get_db),
):
    """Delete a document belonging to a specific notebook."""
    notebook = db.query(Notebook).filter(
        Notebook.id == notebook_id
    ).first()
    if notebook is None:
        raise HTTPException(
            status_code=404,
            detail="Notebook not found.",
        )
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.notebook_id == notebook_id,
        )
        .first()
    )
    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found in this notebook.",
        )
    try:
        delete_document_chunks(
            notebook_id=notebook_id,
            document_id=document_id,
        )
        db.delete(document)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete the document.",
        ) from exc
    return None