# app/rag/retriever.py

from typing import List, Dict
import numpy as np

from ..vectorstore import get_vectorstore  # your FAISS or Chroma wrapper
from .hybrid_search import bm25_search
from .reranker import cross_encoder_rerank
from .context_builder import build_context
from ..llm import answer_with_context


def retrieve_documents(
    query: str,
    top_k_dense: int = 20,
    top_k_sparse: int = 20,
    final_k: int = 8,
) -> Dict:
    """
    Bank-grade hybrid retrieval pipeline:
    1. Dense search via vectorstore (OpenAI embeddings)
    2. Sparse BM25 search (Pyserini)
    3. Weighted hybrid merge
    4. Optional neural reranking
    5. Context builder
    6. LLM answer generator
    """

    # 1️⃣ Dense vector search
    vs = get_vectorstore()
    dense_results = vs.similarity_search_with_score(query, k=top_k_dense)

    dense_docs = [
        {"content": doc.page_content, "score": float(score), "source": "dense"}
        for doc, score in dense_results
    ]

    # 2️⃣ Sparse BM25 search
    sparse_results = bm25_search(query, top_k_sparse)

    # Format to consistent shape
    sparse_docs = [
        {"content": r["content"], "score": float(r["score"]), "source": "sparse"}
        for r in sparse_results
    ]

    # 3️⃣ Weighted hybrid scoring
    hybrid = []
    for d in dense_docs:
        hybrid.append({
            "content": d["content"],
            "score": 0.6 * d["score"],   # dense weight
            "source": d["source"],
        })

    for s in sparse_docs:
        hybrid.append({
            "content": s["content"],
            "score": 0.4 * s["score"],  # sparse weight
            "source": s["source"],
        })

    # Sort descending
    hybrid_sorted = sorted(hybrid, key=lambda x: x["score"], reverse=True)

    # Take top candidates for reranking
    candidate_docs = hybrid_sorted[:final_k * 2]

    # 4️⃣ Neural reranking (cross encoder)
    reranked = cross_encoder_rerank(query, candidate_docs)

    # Keep only final_k
    reranked = reranked[:final_k]

    # Extract plain text
    top_chunks = [d["content"] for d in reranked]

    # 5️⃣ Build final context window
    context = build_context(top_chunks)

    # 6️⃣ Generate LLM answer
    answer = answer_with_context(query, context)

    # Return rich response
    return {
        "query": query,
        "answer": answer,
        "context": top_chunks,
        "num_chunks": len(top_chunks),
    }
