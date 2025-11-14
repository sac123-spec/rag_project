# app/api.py

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings
from .ingestion import ingest_pdfs
from .rag.retriever import retrieve_documents
from .llm import answer_with_context
from .models.reranker_training import train_reranker  # NEW IMPORT

settings = Settings()

app = FastAPI(title="RAG System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Serve UI
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(index_path)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest_endpoint():
    num_docs, num_chunks = ingest_pdfs(settings.raw_dir)
    return {"message": "Ingestion complete", "documents": num_docs, "chunks": num_chunks}


@app.post("/query")
def query_endpoint(payload: dict):
    question = payload.get("query", "")
    if not question:
        return {"error": "Query cannot be empty"}

    retrieved_docs = retrieve_documents(question)
    context = "\n\n".join([d.page_content for d in retrieved_docs])
    answer = answer_with_context(question, context)

    return {"answer": answer, "context_documents": len(retrieved_docs)}


# ---------------------------------------------------
# NEW: Train Reranker Endpoint
# ---------------------------------------------------
@app.post("/train/reranker")
def train_reranker_endpoint():
    logs = train_reranker()
    return {"message": "Training complete", "logs": logs}
