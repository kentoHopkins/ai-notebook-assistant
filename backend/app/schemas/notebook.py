from pydantic import BaseModel, Field
from datetime import datetime

class NotebookCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
        description="The title of the notebook",
    )
    description: str | None = Field(
        default=None,
        description="An optional description of the notebook",
    )

class NotebookUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="The updated title of the notebook",
    )
    description: str | None = Field(
        default=None,
        description="The updated description of the notebook",
    )

class NotebookResponse(BaseModel):
    id: int
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

