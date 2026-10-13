from pydantic import BaseModel, Field

class SummaryResponse(BaseModel):
    notebook_id: int
    summary: str
    source_count: int

class StudyGuideResponse(BaseModel):
    notebook_id: int
    study_guide: str
    source_count: int

class QuizQuestion(BaseModel):
    question: str
    options: dict[str, str]
    correct_answer: str
    explanation: str

class QuizResponse(BaseModel):
    notebook_id: int
    quiz: list[QuizQuestion]
    source_count: int

class QuizRequest(BaseModel):
    num_questions: int = Field(default=5, ge=1, le=20)