import glob
import os
from typing import List, Tuple, Optional

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from .config import settings
from .chunking import split_documents
from .vectorstore import build_vectorstore


def load_pdfs_from_directory(directory: str) -> List[Document]:
    pdf_paths = glob.glob(os.path.join(directory, "*.pdf"))
    docs: List[Document] = []
    for path in pdf_paths:
        loader = PyPDFLoader(path)
        pdf_docs = loader.load()
        for d in pdf_docs:
            d.metadata["source"] = os.path.basename(path)
        docs.extend(pdf_docs)
    return docs


def ingest_pdfs(raw_dir: Optional[str] = None) -> Tuple[int, int]:
    raw_dir = raw_dir or settings.raw_dir

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(settings.chroma_dir, exist_ok=True)

    docs = load_pdfs_from_directory(raw_dir)
    if not docs:
        raise RuntimeError(
            f"No PDFs found in {raw_dir}. Drop PDFs there and run again."
        )

    chunks = split_documents(docs)
    build_vectorstore(chunks, persist_directory=settings.chroma_dir)

    return len(docs), len(chunks)


if __name__ == "__main__":
    n_docs, n_chunks = ingest_pdfs()
    print(f"Ingested {n_docs} original docs into {n_chunks} chunks.")
