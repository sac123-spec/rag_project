from langchain_openai import OpenAIEmbeddings

from .config import settings


def get_embedding_model() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        api_key=settings.openai_api_key,
    )
