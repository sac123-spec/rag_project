from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Generator

# Load backend/.env
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key missing in backend/.env")
    return OpenAI(api_key=api_key)


def _build_context(retrieved: List[dict]) -> str:
    parts: List[str] = []
    for doc in retrieved:
        text = doc.get("text", "")
        source = doc.get("source", "unknown")
        page = doc.get("page", None)
        prefix = f"[{source}"
        if page is not None:
            prefix += f", page {page}"
        prefix += "]"
        parts.append(f"{prefix}\n{text}")
    return "\n\n".join(parts)


def generate_answer(query: str, retrieved: List[dict]) -> str:
    """
    Non-streaming answer generation using backend-only API key.
    """
    client = _get_client()
    model_name = "gpt-4o"  # change model here if you like

    context = _build_context(retrieved)

    prompt = f"""
You are a precise RAG assistant for enterprises.

Use ONLY the context below to answer the user's question.
If the context is insufficient, say "I do not have enough information from the documents."

Context:
{context}

Question:
{query}

Answer:
"""

    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    return completion.choices[0].message.content.strip()


def stream_answer(query: str, retrieved: List[dict]) -> Generator[str, None, None]:
    """
    Streaming answer generator. Yields small text chunks as they arrive from OpenAI.
    """
    client = _get_client()
    model_name = "gpt-4o"

    context = _build_context(retrieved)

    prompt = f"""
You are a precise RAG assistant for enterprises.

Use ONLY the context below to answer the user's question.
If the context is insufficient, say "I do not have enough information from the documents."

Context:
{context}

Question:
{query}

Answer (streaming):
"""

    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        stream=True,
    )

    for chunk in stream:
        choice = chunk.choices[0]
        delta = choice.delta
        if delta and delta.content:
            yield delta.content
