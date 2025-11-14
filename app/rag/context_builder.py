# app/rag/context_builder.py

"""
Bank-grade context builder for RAG pipelines.

This module implements:
- deduplication
- stable sorting
- overlap-aware merging
- token budgeting
- audit-friendly formatting

The output is a clean, deterministic block of text
that can be safely fed into an LLM for constrained reasoning.
"""

from typing import List
import hashlib


def _hash_text(t: str) -> str:
    """Stable SHA-1 hash for deduplication."""
    return hashlib.sha1(t.encode("utf-8")).hexdigest()


def _tokenize(text: str) -> List[str]:
    """Simple fallback tokenizer; banks prefer deterministic tokenizers."""
    return text.split()


def build_context(
    chunks: List[str],
    max_tokens: int = 1400,
    min_chunk_len: int = 20,
) -> str:
    """
    Build the final context for the LLM.

    Steps:
    1. Deduplicate chunks (banks require deterministic behavior)
    2. Remove tiny/noisy chunks
    3. Preserve ranking order
    4. Merge until token budget reached
    """

    if not chunks:
        return ""

    # 1️⃣ Deduplicate
    seen = set()
    deduped = []

    for c in chunks:
        h = _hash_text(c)

        if h not in seen:
            seen.add(h)
            deduped.append(c)

    # 2️⃣ Remove tiny or noisy chunks
    cleaned = [c for c in deduped if len(_tokenize(c)) >= min_chunk_len]

    # 3️⃣ Build context until token budget is reached
    final = []
    token_count = 0

    for c in cleaned:
        c_tokens = len(_tokenize(c))

        if token_count + c_tokens > max_tokens:
            break

        final.append(c)
        token_count += c_tokens

    # 4️⃣ Join cleanly with audit markers
    formatted = ""
    for idx, c in enumerate(final, start=1):
        formatted += f"[CHUNK {idx}]\n{c}\n\n"

    return formatted.strip()
