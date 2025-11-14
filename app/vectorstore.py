# app/vectorstore.py

import os
from typing import Optional, List

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from .config import Settings

settings = Settings()

_VECTORSTORE: Optional[Chroma] = None


def _load_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )


def get_vectorstore() -> Chroma:
    """
    Returns a singleton Chroma vectorstore.
    Creates or loads it from disk.
    """
    global _VECTORSTORE

    if _VECTORSTORE is not None:
        return _VECTORSTORE

    persist_dir = os.path.join(settings.data_dir, "chroma")
    os.makedirs(persist_dir, exist_ok=True)

    embeddings = _load_embeddings()

    _VECTORSTORE = Chroma(
        collection_name="rag_docs",
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    return _VECTORSTORE


def add_documents(docs: List[Document]) -> None:
    """
    Add new documents to the vectorstore and persist it.
    """
    vs = get_vectorstore()
    vs.add_documents(docs)
    vs.persist()
