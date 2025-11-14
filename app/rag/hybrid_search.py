# app/rag/hybrid_search.py

"""
Bank-grade BM25 sparse search implementation.

This version does NOT rely on Pyserini or Java.
It is a pure-Python BM25 implementation compatible with
Python 3.9 and works completely offline.

It loads documents from your Chroma vectorstore and
builds a sparse index on startup.
"""

import math
from typing import List, Dict
from collections import defaultdict

from ..vectorstore import get_vectorstore


# -------------------------
# In-memory BM25 index
# -------------------------

BM25_INDEX = None
BM25_DOCS = None
AVG_DOC_LEN = 0.0


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in text.split()]


def _build_bm25_index():
    """
    Build an in-memory BM25 index from all documents in vectorstore.
    Called automatically when bm25_search() is first used.
    """

    global BM25_INDEX, BM25_DOCS, AVG_DOC_LEN

    vs = get_vectorstore()

    # Pull ALL documents from Chroma
    # (Bank-grade systems sometimes store a sparse index separately)
    all_docs = vs.get(include=["documents"])["documents"]

    BM25_DOCS = all_docs

    # Document frequencies
    df = defaultdict(int)

    tokenized_docs = []
    doc_lengths = []

    for text in all_docs:
        tokens = _tokenize(text)
        tokenized_docs.append(tokens)

        doc_lengths.append(len(tokens))

        # Count unique tokens for DF
        unique_tokens = set(tokens)
        for t in unique_tokens:
            df[t] += 1

    AVG_DOC_LEN = sum(doc_lengths) / max(len(doc_lengths), 1)

    # Build index
    index = defaultdict(dict)

    N = len(all_docs)

    for doc_id, tokens in enumerate(tokenized_docs):
        tf = defaultdict(int)

        for tok in tokens:
            tf[tok] += 1

        for tok, freq in tf.items():
            # BM25 parameters
            k1 = 1.5
            b = 0.75

            df_tok = df[tok]
            idf = math.log(1 + (N - df_tok + 0.5) / (df_tok + 0.5))

            score = idf * ((freq * (k1 + 1)) /
                           (freq + k1 * (1 - b + b * (len(tokens) / AVG_DOC_LEN))))

            index[tok][doc_id] = score

    BM25_INDEX = index


def bm25_search(query: str, k: int = 10) -> List[Dict]:
    """
    Pure Python BM25 search against all documents in vectorstore.

    Output format:
    [
        { "content": "...", "score": 13.24 },
        ...
    ]
    """

    global BM25_INDEX

    if BM25_INDEX is None:
        _build_bm25_index()

    tokens = _tokenize(query)

    doc_scores = defaultdict(float)

    for tok in tokens:
        if tok in BM25_INDEX:
            for doc_id, score in BM25_INDEX[tok].items():
                doc_scores[doc_id] += score

    # Sort by score
    ranked = sorted(
        doc_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Limit results
    ranked = ranked[:k]

    return [
        {"content": BM25_DOCS[doc_id], "score": float(score)}
        for doc_id, score in ranked
    ]
