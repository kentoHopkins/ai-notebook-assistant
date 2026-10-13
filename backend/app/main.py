from fastapi import FastAPI
from backend.app.api.notebooks import router as notebooks_router
from backend.app.api.documents import router as documents_router

app = FastAPI(
    title="AI Notebook Assistant API",
    description="An AI-powered notebook application for document analysis and question answering.",
    version="0.1.0",
)

# Register the notebook API routes.
app.include_router(notebooks_router)
app.include_router(documents_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to AI Notebook Assistant!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
