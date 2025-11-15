from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import os
import json

from backend.vectorstore import list_documents, delete_document, rebuild_index
from backend.ingestion import ingest_pdfs
from backend.rag.retriever import hybrid_retrieve
from backend.rag.reranker import CrossEncoderReranker
from backend.llm import generate_answer, stream_answer
from backend.training import train_crossencoder
from backend.config import DATA_DIR

# -------------------------------------------------------
# FASTAPI APP
# -------------------------------------------------------

app = FastAPI()

# CORS (frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# INITIALIZE RERANKER
# -------------------------------------------------------

reranker = CrossEncoderReranker()

# -------------------------------------------------------
# REQUEST MODELS
# -------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

    class Config:
        extra = "ignore"  # ignore any old openai_api_key sent by frontend


class TrainingSample(BaseModel):
    query: str
    positive_passages: List[str]
    negative_passages: List[str]


class TrainRerankerRequest(BaseModel):
    samples: List[TrainingSample]
    num_epochs: int
    batch_size: int

    class Config:
        extra = "ignore"  # ignore legacy fields if any


# -------------------------------------------------------
# ROUTES
# -------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "message": "RAG backend running"}


# ----------------- DOCUMENTS --------------------------

@app.get("/documents")
def get_docs():
    return {"documents": list_documents()}


@app.post("/documents/upload")
async def upload_docs(files: List[UploadFile] = File(...)):
    os.makedirs(DATA_DIR, exist_ok=True)

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue

        dest_path = os.path.join(DATA_DIR, file.filename)
        content = await file.read()

        with open(dest_path, "wb") as f:
            f.write(content)

    # Ingest PDFs and update vectorstore
    ingest_pdfs()

    return {"documents": list_documents()}


@app.delete("/documents/{filename}")
def delete_file(filename: str):
    delete_document(filename)
    return {"documents": list_documents()}


@app.post("/documents/reindex")
def reindex():
    count = rebuild_index()
    return {"indexed_chunks": count}


# ----------------- QUERY RAG (NON-STREAMING) ----------

@app.post("/query")
def query(req: QueryRequest):
    # Hybrid retrieve
    retrieved = hybrid_retrieve(req.query, req.top_k)

    # Cross-encoder reranking
    reranked = reranker.rerank(req.query, retrieved)

    # Final LLM answer (backend key only)
    answer = generate_answer(
        query=req.query,
        retrieved=reranked
    )

    return {
        "answer": answer,
        "sources": reranked
    }


# ----------------- QUERY RAG (STREAMING) --------------

@app.post("/query-stream")
def query_stream(req: QueryRequest):
    """
    Streaming endpoint.
    Sends JSON lines:
      {"type": "token", "content": "..."}
      {"type": "meta", "sources": [...]}
    """

    # Hybrid retrieve & rerank once
    retrieved = hybrid_retrieve(req.query, req.top_k)
    reranked = reranker.rerank(req.query, retrieved)

    def event_generator():
        # Stream tokens
        for token in stream_answer(req.query, reranked):
            msg = json.dumps({"type": "token", "content": token})
            yield msg + "\n"

        # After streaming completes, send metadata (sources)
        meta = json.dumps({"type": "meta", "sources": reranked})
        yield meta + "\n"

    return StreamingResponse(event_generator(), media_type="text/plain")


# ----------------- TRAIN RERANKER ---------------------

@app.post("/train-reranker")
def train_reranker(req: TrainRerankerRequest):
    model_path = train_crossencoder(
        samples=req.samples,
        epochs=req.num_epochs,
        batch_size=req.batch_size,
    )

    return {"status": "ok", "model_path": model_path}
