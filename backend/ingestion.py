import os
import glob
from backend.config import DATA_DIR
from backend.rag.chunking import chunk_pdf


def ingest_pdfs():
    os.makedirs(DATA_DIR, exist_ok=True)
    pdf_files = glob.glob(f"{DATA_DIR}/*.pdf")

    for pdf in pdf_files:
        chunk_pdf(pdf)
