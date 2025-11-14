from typing import List, Optional
from langchain_core.documents import Document

from .config import settings
from .vectorstore import load_vectorstore
from .embeddings import get_embedding_model
from .models.reranker import Reranker


def get_retriever():
    vs = load_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": settings.top_k})
    return retriever


def retrieve_documents(
    query: str,
    top_k: Optional[int] = None,
    use_reranker: Optional[bool] = None,
) -> List[Document]:

    top_k = top_k or settings.top_k
    use_reranker = (
        settings.use_reranker_by_default if use_reranker is None else use_reranker
    )

    vs = load_vectorstore()
    base_k = max(top_k * 3, top_k)
    raw_docs = vs.similarity_search(query, k=base_k)

    if not use_reranker:
        return raw_docs[:top_k]

    # If model does not exist, fallback
    from pathlib import Path
    model_path = Path(settings.reranker_model_path)
    if not model_path.exists():
        return raw_docs[:top_k]

    embedding_model = get_embedding_model()
    reranker = Reranker.from_pretrained(
        embedding_model=embedding_model,
        model_path=str(model_path),
        device="cpu",
    )

    reranked = reranker.rerank(query, raw_docs, top_k=top_k)
    return reranked
