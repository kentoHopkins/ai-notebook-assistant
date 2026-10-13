from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import mapped_column
from backend.app.database import Base
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = mapped_column(Integer, primary_key=True)
    notebook_id = mapped_column(
        Integer,
        ForeignKey("notebooks.id"),
        nullable=False,
        index=True,
    )
    role = mapped_column(
        String(20),
        nullable=False,
    )
    content = mapped_column(
        Text,
        nullable=False,
    )
    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class ChatMessageResponse(BaseModel):
    id: int
    notebook_id: int
    role: str
    content: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)