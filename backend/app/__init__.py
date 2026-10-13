from backend.app.database import Base, engine
from backend.app.models.notebook import Notebook
from backend.app.models.document import Document

def init_db():
    """Create database tables for all registered models."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")