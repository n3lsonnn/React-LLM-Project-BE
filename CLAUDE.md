# DocuWise — Backend Context

## What this project is
DocuWise is a full-stack RAG (Retrieval-Augmented Generation) document 
intelligence platform. Users upload PDFs and chat with them in natural 
language. Answers stream in real time with citations showing exactly 
which part of the document the answer came from.

This file covers the BACKEND only. The frontend lives in a separate 
repo: React-LLM-Project-FE.

## How the two repos connect
- The frontend calls this backend at its deployed Railway URL
- The backend must have CORS configured to allow requests from the 
  frontend's Vercel URL
- The join points are:
    POST /auth/register
    POST /auth/login
    POST /documents/upload
    GET  /documents/
    GET  /documents/{id}/status
    POST /chat/query          ← streams SSE tokens back to frontend
- The frontend sends a Bearer JWT token in the Authorization header 
  on every protected request
- The backend validates that token using the get_current_user 
  dependency on all protected routes

## My background
- MSc Artificial Intelligence with Distinction, University of South Wales
- Dissertation was a RAG chatbot for aviation Structural Repair Manuals
  — this backend is that pipeline productised into a web API
- Internship at FTAI Aviation as Full Stack Developer (React + REST 
  APIs + Oracle/SQL Server on private Azure repos)
- OS: Windows, developing locally then deploying to Railway

## Tech stack
- Framework: FastAPI (Python 3.11)
- Database: PostgreSQL via Supabase (connection string in .env)
- ORM: SQLAlchemy
- Migrations: Alembic
- Auth: JWT via python-jose, passwords hashed with passlib bcrypt
- Embeddings: sentence-transformers all-MiniLM-L6-v2
- Vector search: FAISS (IndexFlatL2, exact search)
- LLM: Groq API with streaming enabled (replaces Ollama from 
  dissertation for speed — was 40s latency, now under 2s)
- Linting: Ruff
- Testing: pytest + httpx
- Deployment: Railway (Procfile: uvicorn main:app --host 0.0.0.0 
  --port $PORT)

## Folder structure
app/
  api/routes/      ← auth.py, documents.py, chat.py (HTTP layer only)
  core/            ← config.py, database.py, security.py, deps.py
  models/          ← SQLAlchemy table definitions
  schemas/         ← Pydantic request/response shapes
  services/        ← ingestion.py, query.py (all business logic here)
alembic/           ← migration files, never edit manually
tests/             ← pytest test files
indexes/           ← FAISS .faiss and .json files, named by document UUID
main.py            ← FastAPI app, registers routers, adds middleware
requirements.txt
Procfile
.env               ← never committed to GitHub

## Environment variables needed in .env
DATABASE_URL=postgresql://...
SECRET_KEY=long-random-string
GROQ_API_KEY=gsk_...
FRONTEND_URL=http://localhost:5173  ← update to Vercel URL in production

## Key architecture decisions
- Routes only handle HTTP — all logic lives in services/
- Pydantic Settings in config.py validates env vars at startup
- JWT stored in frontend memory, not cookies or localStorage
- PDF ingestion runs as a background task (returns 202 immediately,
  polls /documents/{id}/status until status="ready")
- FAISS indexes saved as files: indexes/{document_uuid}.faiss 
  and indexes/{document_uuid}.json
- SSE (Server-Sent Events) used for streaming, not WebSockets
- Each SSE event is JSON: {"token": "word", "done": false}
  Final event: {"citations": [...], "done": true}
- Global exception handler returns consistent JSON error shape:
  {"detail": "message", "code": "ERROR_CODE"}

## 12-day plan — backend days
Day 1: Install tools, create venv, first health endpoint running
Day 2: Folder structure, Supabase connection, Alembic init
Day 3: User model, bcrypt hashing, JWT issue/verify, 
        register + login routes
Day 5: Ingestion service — PDF extract, chunking, embeddings, 
        FAISS index build, upload endpoint
Day 6: Query service — FAISS retrieval, prompt assembly, 
        Groq streaming endpoint via SSE
Day 9: Ruff linting, pytest tests, GitHub Actions CI workflow
Day 10: Deploy to Railway, set environment variables in dashboard

## How to run locally
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
# API runs at http://localhost:8000
# Auto-generated docs at http://localhost:8000/docs