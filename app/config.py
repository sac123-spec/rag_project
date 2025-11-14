# app/config.py

import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    App configuration using Pydantic v2
    """

    # ------------------------
    # Directory paths
    # ------------------------
    base_dir: str = Field(default_factory=lambda: os.path.dirname(os.path.abspath(__file__)))
    data_dir: str = Field(default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
    raw_dir: str = Field(default_factory=lambda: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw"))

    # ------------------------
    # LLM / Embeddings
    # ------------------------
    openai_api_key: str = Field(default=os.getenv("OPENAI_API_KEY", ""))
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    # ------------------------
    # App settings
    # ------------------------
    debug: bool = False

    class Config:
        env_file = ".env"
