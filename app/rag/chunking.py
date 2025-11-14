# app/rag/chunking.py

import nltk
from typing import List

# Ensure sentence tokenizer exists
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")


def split_into_sentences(text: str) -> List[str]:
    """
    Breaks raw text into sentences.
    """
    sentences = nltk.sent_tokenize(text)
    return [s.strip() for s in sentences if s.strip()]


def semantic_adaptive_chunk(
    text: str,
    max_tokens: int = 350,
    min_tokens: int = 80,
    overlap_tokens: int = 40,
    tokenizer=None,
) -> List[str]:
    """
    Bank-grade chunking:
    - sentence-level segmentation
    - dynamic windowing
    - soft overlap
    """

    # Basic fallback tokenizer
    if tokenizer is None:
        tokenizer = lambda s: len(s.split())

    sentences = split_into_sentences(text)

    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sent_len = tokenizer(sentence)

        # Hard split very long sentences
        if sent_len > max_tokens:
            words = sentence.split()
            temp = []
            count = 0

            for w in words:
                if count + 1 > max_tokens:
                    chunks.append(" ".join(temp))
                    temp = []
                    count = 0
                temp.append(w)
                count += 1

            if temp:
                chunks.append(" ".join(temp))

            continue

        # Create new chunk if window is exceeded
        if current_len + sent_len > max_tokens:
            chunks.append(" ".join(current_chunk).strip())
            current_chunk = [sentence]
            current_len = sent_len
        else:
            current_chunk.append(sentence)
            current_len += sent_len

    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())

    # Merge small chunks
    merged = []
    for c in chunks:
        if not merged:
            merged.append(c)
            continue

        if len(merged[-1].split()) < min_tokens:
            merged[-1] = merged[-1] + " " + c
        else:
            merged.append(c)

    # Apply overlap
    final_chunks = []
    for idx, c in enumerate(merged):
        if idx == 0:
            final_chunks.append(c)
            continue

        prev_words = merged[idx - 1].split()
        overlap = " ".join(prev_words[-overlap_tokens:])
        final_chunks.append(f"{overlap} {c}".strip())

    return final_chunks
