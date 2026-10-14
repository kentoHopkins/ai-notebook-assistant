# AI Notebook Assistant

AI Notebook Assistant is a full-stack application inspired by NotebookLM. It lets users organize their materials into notebooks, add documents or webpage content, and ask questions based on the information they provide.

I built this project to explore how retrieval-augmented generation (RAG) can be used to make AI responses more relevant to a user's own documents instead of relying only on the language model's existing knowledge.

## Live Demo

- **Frontend:** https://ai-notebook-assistant-h9s8.onrender.com
- **Backend API:** https://ai-notebook-assistant-api.onrender.com
- **API Documentation:** https://ai-notebook-assistant-api.onrender.com/docs
- **GitHub Repository:** https://github.com/kentoHopkins/ai-notebook-assistant

The hosted application depends on the backend service and its available resources. If the backend is starting up or has run into resource limits, some features may not respond immediately.

## Features

### Notebook Management
- Create and organize multiple notebooks.
- Keep source material associated with a notebook.
- Use notebook content as the basis for questions and generated study materials.

### Document Ingestion
- Upload PDF, PowerPoint (`.pptx`), and text (`.txt`) files.
- Import content from a public webpage URL.
- Extract text from supported sources.
- Split extracted text into smaller chunks for retrieval.
- Associate source information with document chunks.

### Question Answering
- Ask questions about the content in a notebook.
- Retrieve relevant document chunks using vector search.
- Provide retrieved content to the language model as context.
- Use source references to help users check where information comes from.

### Study Materials
The application is designed to help users work with their notebook content beyond basic question answering. Available artifact-generation features depend on the current implementation and deployment.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Backend | Python, FastAPI |
| Relational database | SQLAlchemy, SQLite by default |
| Vector database | ChromaDB |
| Embedding model | ONNX MiniLM (`all-MiniLM-L6-v2`) |
| Text processing | BeautifulSoup, LangChain text splitters |
| Language model API | Groq |
| Testing | pytest |
| CI | GitHub Actions |
| Hosting | Render |

## How It Works

The application uses retrieval-augmented generation (RAG) to answer questions using information from the user's sources.

The workflow is:

1. **Add a source.** The user uploads a supported file or provides a public webpage URL.
2. **Extract the text.** The backend processes the source and extracts its readable content.
3. **Split the content.** The extracted text is divided into smaller chunks so relevant passages can be retrieved later.
4. **Create embeddings.** The embedding model converts the chunks into vector representations.
5. **Store the chunks.** ChromaDB stores the vectors and associated source information.
6. **Ask a question.** The user submits a question about the notebook.
7. **Retrieve relevant content.** The backend searches for chunks related to the question.
8. **Generate an answer.** The retrieved content is passed to the language model as context.
9. **Return the result.** The application displays the generated response and available source references.

Using this approach helps connect answers to the original material. However, retrieval does not guarantee that every answer is correct, so the quality of the retrieved passages and the generated response still needs to be evaluated.

## Architecture

The application separates the frontend, backend API, document-processing pipeline, and data-storage components.

### Frontend
The React application provides the interface for managing notebooks, adding sources, asking questions, and viewing results. It communicates with the backend through HTTP requests.

### Backend API
FastAPI handles application requests and connects the frontend to the underlying services. It coordinates document ingestion, retrieval, and response generation.

### Document Processing
The ingestion pipeline extracts text from supported files and webpages. The text is split into chunks before being passed to the embedding and storage components.

### Vector Storage
ChromaDB stores document embeddings and associated metadata. When a question is submitted, the backend uses retrieval to identify potentially relevant passages.

### Relational Storage
SQLAlchemy provides the application's relational data-access layer, with SQLite used by default. The relational database and vector store serve different purposes: relational storage handles structured application data, while ChromaDB supports semantic retrieval.

### Language Model
The backend uses Groq to access a language model for generating responses from retrieved context.

### Data Flow

```text
                 User
                  |
                  v
          React Frontend
                  |
                  v
             FastAPI
                  |
          +-------+-------+
          |               |
          v               v
   Document Ingestion   User Question
          |               |
          v               v
    Text Extraction   Query Embedding
          |               |
          v               v
    Text Chunking     ChromaDB Search
          |               |
          v               v
    Embeddings       Retrieved Chunks
          |               |
          v               v
       ChromaDB ------> Groq LLM
                           |
                           v
                   Generated Answer
                           |
                           v
                    React Frontend
```

The relational database separately stores structured application data. The exact persistence of application data and vector data depends on the configured database and storage environment.

For more details, see [`docs/architecture.md`](docs/architecture.md).

## Running the Project Locally

### Requirements

- Python 3.10 or newer
- Node.js and npm
- A Groq API key

### 1. Clone the repository

```bash
git clone https://github.com/kentoHopkins/ai-notebook-assistant.git
cd ai-notebook-assistant
```

### 2. Set up the backend

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the backend dependencies from the directory containing the project's Python requirements file:

```bash
pip install -r requirements.txt
```

Create a `.env` file and configure the environment variables required by the backend. For example:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_configured_groq_model
DATABASE_URL=sqlite:///./data/app.db
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHROMA_PERSIST_DIRECTORY=./data/chroma
```

These values are examples. Check the application's configuration and use the variable names and defaults expected by the current code.

Start the backend from the repository root if its entry point is `backend.app.main:app`:

```bash
uvicorn backend.app.main:app --reload
```

The API should be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation should be available at:

```text
http://127.0.0.1:8000/docs
```

### 3. Set up the frontend

Open another terminal and move into the frontend directory:

```bash
cd frontend
npm install
```

Create a frontend environment file if required:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Open the local address printed by Vite in the terminal.

Make sure the frontend API URL and backend CORS configuration match your local setup.

## Testing

The backend tests can be run with pytest:

```bash
python -m pytest -v
```

The test suite previously passed with 31 tests. Run it again against the final version before submitting.

GitHub Actions is configured for automated checks. The latest workflow result can be found in the repository's **Actions** tab.

A passing local test suite does not automatically mean the deployed application is working correctly. The hosted frontend and backend should also be tested together.

## RAG Evaluation

An important part of this project is evaluating how well retrieval supports question answering.

The evaluation should compare two retrieval approaches using the same source documents and test questions. The comparison should consider:

- Which chunks each approach retrieves.
- How long retrieval takes.
- Whether the retrieved chunks contain evidence relevant to the question.
- Whether the generated answer is supported by that evidence.
- Whether the source references point to the correct material.
- The strengths and limitations of each approach.

The final report should include the test questions, retrieved chunks, response times, answer-quality assessments, and conclusions about the trade-offs between the approaches.

See [`docs/rag_evaluation.md`](docs/rag_evaluation.md) for the evaluation results.

*Evaluation measurements and conclusions should be based on actual test runs rather than estimated results.*

## Deployment

The application is deployed using Render.

| Service | URL |
|---|---|
| Frontend | https://ai-notebook-assistant-h9s8.onrender.com |
| Backend | https://ai-notebook-assistant-api.onrender.com |
| API documentation | https://ai-notebook-assistant-api.onrender.com/docs |

The frontend uses `VITE_API_BASE_URL` to identify the backend API. The backend must also allow requests from the deployed frontend through its CORS configuration.

Secrets such as `GROQ_API_KEY` should be configured through the hosting provider's environment settings instead of being committed to GitHub.

The free hosting environment has resource limitations, so document ingestion and embedding operations should be tested on the deployed application before a demonstration.

## Project Documentation

Additional project documentation:

- [System Architecture](docs/architecture.md)
- [RAG Evaluation](docs/rag_evaluation.md)

These documents describe the system design and the results of the retrieval comparison required for the project.

## Limitations

There are a few practical limitations to consider:

- Retrieval quality depends on the source material, chunking strategy, embedding model, and search method.
- Generated answers can still contain mistakes, even when relevant document chunks are retrieved.
- Only supported file types and public, single-page webpage sources are intended for ingestion.
- The hosted environment has resource limits that can affect larger ingestion requests.
- Persistent storage depends on the database and disk configuration used by the deployment.

## Future Improvements

Possible improvements include:

- Evaluating additional retrieval and ranking strategies.
- Improving source citations and answer-grounding checks.
- Making document processing more efficient for larger files.
- Improving persistence and storage management in production.
- Expanding automated tests for ingestion, retrieval, and artifact generation.

## License

No license has been specified. Add a `LICENSE` file if the project is intended to be distributed or reused under an open-source license.
