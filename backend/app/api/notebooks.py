from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.notebook import Notebook
from backend.app.schemas.notebook import (
    NotebookCreate,
    NotebookUpdate,
    NotebookResponse,
)

router = APIRouter(
    prefix="/notebooks",
    tags=["Notebooks"],
)

@router.post(
    "",
    response_model=NotebookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notebook(
    notebook_data: NotebookCreate,
    db: Session = Depends(get_db),
):
    # create new db object
    new_notebook = Notebook(
        title=notebook_data.title,
        description=notebook_data.description,
    )
    try:
        db.add(new_notebook)
        db.commit()
        db.refresh(new_notebook)
    except Exception:
        db.rollback()
        raise
    return new_notebook

@router.get(
    "",
    response_model=list[NotebookResponse],
)
def get_notebooks(
    db: Session = Depends(get_db),
):
    #get all notebooks from the database.
    notebooks = (
        db.query(Notebook)
        .order_by(Notebook.created_at.desc())
        .all()
    )
    return notebooks

@router.get(
    "/{notebook_id}",
    response_model=NotebookResponse,
)
def get_notebook(
    notebook_id: int,
    db: Session = Depends(get_db),
):
    #get the notebook with the requested ID.
    notebook = (
        db.query(Notebook)
        .filter(Notebook.id == notebook_id)
        .first()
    )
    if notebook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    return notebook

@router.patch(
    "/{notebook_id}",
    response_model=NotebookResponse,
)
def update_notebook(
    notebook_id: int,
    notebook_data: NotebookUpdate,
    db: Session = Depends(get_db),
):
    #find the notebook that needs to be updated.
    notebook = (
        db.query(Notebook)
        .filter(Notebook.id == notebook_id)
        .first()
    )
    if notebook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )
    update_data = notebook_data.model_dump(exclude_unset=True)

    #do not accept requests if that contain no fields to update.
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )
    #reject null titles
    if "title" in update_data and update_data["title"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Notebook title cannot be null",
        )
    # change the database object.
    for field, value in update_data.items():
        setattr(notebook, field, value)
    try:
        db.commit()
        db.refresh(notebook)
    except Exception:
        db.rollback()
        raise
    return notebook

@router.delete(
    "/{notebook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notebook(
    notebook_id: int,
    db: Session = Depends(get_db),
):
    #find specific notebook
    notebook = (
        db.query(Notebook)
        .filter(Notebook.id == notebook_id)
        .first()
    )
    if notebook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )

    #delete
    try:
        db.delete(notebook)
        db.commit()

    except Exception:
        db.rollback()
        raise
