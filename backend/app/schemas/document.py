from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

class DocumentURLCreate(BaseModel):
    """Schema for adding a webpage to a notebook."""
    url: HttpUrl = Field(
        ...,
        description="The public webpage URL to import.",
    )

class DocumentResponse(BaseModel):
    """Schema for returning document information to the client."""
    id: int
    notebook_id: int
    filename: str
    source_type: str
    source_url: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)