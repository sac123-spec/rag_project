import os
from pydantic import BaseModel


class Settings(BaseModel):
    # LLM + embeddings
    openai_api_key: str = os.environ.get("OPENAI_API_KEY", "")
    openai_chat_model: str = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
    openai_embedding_model: str = os.environ.get(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )

    # Paths
    base_dir: str = os.environ.get("RAG_BASE_DIR", ".")
    data_dir: str = os.path.join(base_dir, "data")
    raw_dir: str = os.path.join(data_dir, "raw")
    chroma_dir: str = os.path.join(data_dir, "chroma")
    training_dir: str = os.path.join(data_dir, "training")

    # Retrieval
    top_k: int = int(os.environ.get("RAG_TOP_K", 5))
    chunk_size: int = int(os.environ.get("RAG_CHUNK_SIZE", 1000))
    chunk_overlap: int = int(os.environ.get("RAG_CHUNK_OVERLAP", 200))

    # Training / reranker
    reranker_model_path: str = os.path.join(training_dir, "reranker.pt")
    use_reranker_by_default: bool = bool(
        int(os.environ.get("RAG_USE_RERANKER", "0"))
    )


settings = Settings()
