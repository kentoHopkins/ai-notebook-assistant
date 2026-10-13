from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import mapped_column
from backend.app.database import Base

class Document(Base):
    __tablename__ = "documents"
    id = mapped_column(Integer, primary_key=True)
    notebook_id = mapped_column(
        Integer,
        ForeignKey("notebooks.id"),
        nullable=False,
    )
    filename = mapped_column(
        String(255),
        nullable=False,
    )
    source_type = mapped_column(
        String(20),
        nullable=False,
    )
    source_url = mapped_column(
        Text,
        nullable=True,
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