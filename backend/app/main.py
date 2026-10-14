from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.notebooks import router as notebooks_router
from backend.app.api.documents import router as documents_router
from backend.app.api.chat import router as chat_router
from backend.app.api.study_materials import router as study_materials_router

app = FastAPI(
    title="AI Notebook Assistant API",
    description="An AI-powered notebook application for document analysis and question answering.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the notebook API routes.
app.include_router(notebooks_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(study_materials_router)

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
