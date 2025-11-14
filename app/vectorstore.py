from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from .embeddings import get_embedding_model
from .config import settings


def build_vectorstore(
    documents: List[Document],
    persist_directory: Optional[str] = None,
) -> Chroma:
    """Create (or overwrite) a Chroma vector store from documents."""
    persist_directory = persist_directory or settings.chroma_dir
    embedding = get_embedding_model()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory=persist_directory,
    )
    return vectorstore


def load_vectorstore(persist_directory: Optional[str] = None) -> Chroma:
    """Load an existing Chroma store (must exist on disk)."""
    persist_directory = persist_directory or settings.chroma_dir
    embedding = get_embedding_model()
    vectorstore = Chroma(
        embedding_function=embedding,
        persist_directory=persist_directory,
    )
    return vectorstore
