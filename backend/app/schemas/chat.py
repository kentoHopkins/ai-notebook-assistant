from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's question about the notebook documents.",
    )

class SourceCitation(BaseModel):
    document_id: int
    filename: str
    chunk_index: int


class QuestionResponse(BaseModel):
    notebook_id: int
    question: str
    answer: str
    sources: list[SourceCitation]