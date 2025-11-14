# app/ingestion.py

import os
import glob
from typing import List, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document  # LangChain v0.2 compatible

from .config import Settings
from .rag.chunking import semantic_adaptive_chunk
from .vectorstore import add_documents

settings = Settings()


def load_pdfs(raw_dir: Optional[str] = None) -> List[str]:
    """
    Load all PDFs from the raw_dir and return a list of page-level texts.
    Each element in the returned list is the text of one PDF page.
    """
    raw_dir = raw_dir or settings.raw_dir

    pdf_paths = glob.glob(os.path.join(raw_dir, "*.pdf"))
    if not pdf_paths:
        raise RuntimeError(
            "No PDFs found in {}. Drop PDFs there and run again.".format(raw_dir)
        )

    page_texts: List[str] = []

    for path in pdf_paths:
        loader = PyPDFLoader(path)
        pages = loader.load()
        for page in pages:
            if page.page_content:
                page_texts.append(page.page_content)

    return page_texts


def chunk_pages_to_documents(page_texts: List[str]) -> List[Document]:
    """
    Take raw PDF page texts, run them through the semantic chunker,
    and wrap resulting chunks into LangChain Document objects,
    with simple metadata for traceability.
    """
    docs: List[Document] = []

    for page_index, text in enumerate(page_texts):
        # Get chunks for this page
        chunks = semantic_adaptive_chunk(text)

        for chunk_index, chunk in enumerate(chunks):
            metadata = {
                "page_index": page_index,
                "chunk_index": chunk_index,
            }
            docs.append(Document(page_content=chunk, metadata=metadata))

    return docs


def ingest_pdfs(raw_dir: Optional[str] = None):
    """
    Main ingestion pipeline:
    1. Load raw PDFs into page texts
    2. Chunk pages into semantic chunks
    3. Turn chunks into Document objects
    4. Push Documents into the vectorstore

    Returns:
      (num_pdfs, num_chunks)
    """
    raw_dir = raw_dir or settings.raw_dir

    # Count PDFs
    pdf_paths = glob.glob(os.path.join(raw_dir, "*.pdf"))
    num_pdfs = len(pdf_paths)

    if num_pdfs == 0:
        raise RuntimeError(
            "No PDFs found in {}. Drop PDFs there and run again.".format(raw_dir)
        )

    # 1) Load pages
    page_texts = load_pdfs(raw_dir)

    # 2) Chunk pages and build Documents
    docs = chunk_pages_to_documents(page_texts)

    # 3) Store in vectorstore
    if docs:
        add_documents(docs)

    num_chunks = len(docs)

    return num_pdfs, num_chunks
