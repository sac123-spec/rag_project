from typing import Optional, List, Dict
from pathlib import Path
import shutil
import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .config import settings
from .ingestion import ingest_pdfs
from .retrieval import retrieve_documents
from .llm import generate_answer


# ---------- Pydantic models ----------

class IngestResponse(BaseModel):
    num_raw_docs: int
    num_chunks: int


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None
    use_reranker: Optional[bool] = None


class SourceItem(BaseModel):
    content: str
    metadata: Dict


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]


class DeleteFilesRequest(BaseModel):
    filenames: List[str]


class FilesListResponse(BaseModel):
    files: List[Dict]


class RebuildResponse(BaseModel):
    num_raw_docs: int
    num_chunks: int


# ---------- FastAPI app ----------

app = FastAPI(title="RAG Semantic Search API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Serve static frontend files
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", response_class=FileResponse)
def serve_index():
    """
    Serve the dashboard UI.
    """
    return FileResponse(str(INDEX_FILE))


# ---------- Core API: health, upload, ingest, query ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload one or more PDF files to data/raw.
    """
    saved_files: List[str] = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            # skip non-PDFs silently
            continue

        dest = RAW_DIR / file.filename
        with dest.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_files.append(file.filename)

    return {"saved": saved_files}


@app.post("/ingest", response_model=IngestResponse)
def ingest_endpoint():
    """
    Ingest PDFs from data/raw into the vector store.
    """
    n_docs, n_chunks = ingest_pdfs(str(RAW_DIR))
    return IngestResponse(num_raw_docs=n_docs, num_chunks=n_chunks)


@app.post("/query", response_model=QueryResponse)
def query_endpoint(payload: QueryRequest):
    """
    Run semantic search + RAG answer.
    """
    docs = retrieve_documents(
        query=payload.question,
        top_k=payload.top_k,
        use_reranker=payload.use_reranker,
    )

    answer = generate_answer(payload.question, docs)

    sources = [
        SourceItem(content=d.page_content, metadata=d.metadata)
        for d in docs
    ]

    return QueryResponse(answer=answer, sources=sources)


# ---------- Admin API: list, delete, rebuild ----------

@app.get("/admin/files", response_model=FilesListResponse)
def list_pdfs():
    """
    List PDF files currently in data/raw.
    """
    files: List[Dict] = []
    for p in RAW_DIR.glob("*.pdf"):
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        files.append(
            {
                "name": p.name,
                "size": size,
            }
        )
    return FilesListResponse(files=files)


@app.post("/admin/delete")
def delete_pdfs(payload: DeleteFilesRequest):
    """
    Delete a list of PDFs from data/raw.
    """
    deleted: List[str] = []
    missing: List[str] = []

    for fname in payload.filenames:
        path = RAW_DIR / fname
        if path.exists():
            try:
                path.unlink()
                deleted.append(fname)
            except OSError:
                missing.append(fname)
        else:
            missing.append(fname)

    return {"deleted": deleted, "missing": missing}


@app.post("/admin/rebuild", response_model=RebuildResponse)
def rebuild_vectorstore():
    """
    Remove existing vector store and rebuild from current PDFs in data/raw.
    """
    chroma_path = Path(settings.chroma_dir)

    if chroma_path.exists():
        shutil.rmtree(chroma_path)
    os.makedirs(chroma_path, exist_ok=True)

    n_docs, n_chunks = ingest_pdfs(str(RAW_DIR))

    return RebuildResponse(num_raw_docs=n_docs, num_chunks=n_chunks)
