import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# Read the database URL from the environment.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/app.db",
)

#since SQLite stores its database in a file, the parent directory must exist before SQLite can create the database file
if DATABASE_URL.startswith("sqlite:///"):
    database_path = DATABASE_URL.removeprefix("sqlite:///")
    #skip directory creation for an in-memory database. For relative path, create the parent directory under PROJECT_ROOT
    if database_path != ":memory:" and not database_path.startswith("/"):
        (PROJECT_ROOT / Path(database_path).parent).mkdir(
            parents=True,
            exist_ok=True,
        )

#SQLlite restricts a connection to the tread that created it so disable particular restriction for SQLite.
connect_args = (
    {"check_same_thread": False} 
    if DATABASE_URL.startswith("sqlite") 
    else {}
)

# Create a shared SQLAlchemy engine.
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

#create a factory for database sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

class Base(DeclarativeBase):
    pass

def get_db():
    """Provide a database session and close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.app import models
    Base.metadata.create_all(bind=engine)