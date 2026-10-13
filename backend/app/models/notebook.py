from sqlalchemy import Integer, String, Text, DateTime, func
from sqlalchemy.orm import mapped_column
from backend.app.database import Base

class Notebook(Base):
    __tablename__ = "notebooks"

    #id, title and description for each notebook.
    id = mapped_column(Integer, primary_key=True)
    title = mapped_column(String(200), nullable=False)
    description = mapped_column(Text, nullable=True)

    # Timestamp
    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )