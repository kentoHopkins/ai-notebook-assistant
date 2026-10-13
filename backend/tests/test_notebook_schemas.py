import pytest
from pydantic import ValidationError

from backend.app.schemas.notebook import (
    NotebookCreate,
    NotebookUpdate,
    NotebookResponse,
)

def test_create_notebook_with_title():
    #testing if notebook creation works properly
    notebook = NotebookCreate(
        title="Machine Learning Research",
    )
    assert notebook.title == "Machine Learning Research"
    assert notebook.description is None

def test_create_notebook_with_description():
    #testing if notebook creation with discription
    notebook = NotebookCreate(
        title="Machine Learning Research",
        description="Research papers about machine learning",
    )

    assert notebook.title == "Machine Learning Research"
    assert notebook.description == "Research papers about machine learning"

def test_create_notebook_without_title():
    #testing if notebook creation will get rejected when title is missing
    with pytest.raises(ValidationError):
        NotebookCreate(
            description="Research papers about machine learning",
        )

def test_create_notebook_with_empty_title():
    #testing if notebook creation with empty title. It should get rejected since min length for title is 1.
    with pytest.raises(ValidationError):
        NotebookCreate(title="")

def test_update_notebook_with_title_only():
    #testing notebook title update
    notebook = NotebookUpdate(
        title="Deep Learning Research",
    )
    assert notebook.title == "Deep Learning Research"
    assert notebook.description is None

def test_update_notebook_with_description_only():
    #testing notebook description update
    notebook = NotebookUpdate(
        description="Updated research notes",
    )
    assert notebook.title is None
    assert notebook.description == "Updated research notes"

def test_update_notebook_with_empty_title():
    #testing notebook title update with empty title which should get rejected
    with pytest.raises(ValidationError):
        NotebookUpdate(title="")

def test_notebook_response_from_attributes():
    #testing notebook response
    class FakeNotebook:
        id = 1
        title = "Machine Learning Research"
        description = "Research papers about machine learning"
        created_at = "2026-10-12T12:00:00"
        updated_at = "2026-10-12T12:00:00"

    notebook = NotebookResponse.model_validate(
        FakeNotebook(),
    )
    assert notebook.id == 1
    assert notebook.title == "Machine Learning Research"
    assert notebook.description == "Research papers about machine learning"