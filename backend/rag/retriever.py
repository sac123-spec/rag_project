from backend.vectorstore import collection
from backend.rag.bm25 import bm25_search

def hybrid_retrieve(query: str, top_k: int = 5):
    """
    Hybrid retrieval combining:
    - Dense vector search (Chroma)
    - BM25 keyword search
    """

    # ---- Dense search from Chroma ----
    dense_results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    dense_docs = []
    for i in range(len(dense_results["documents"][0])):
        dense_docs.append({
            "text": dense_results["documents"][0][i],
            "score": float(dense_results["distances"][0][i]),
            "source": dense_results["metadatas"][0][i]["source"],
            "page": dense_results["metadatas"][0][i]["page"],
            "chunk_index": i
        })

    # ---- BM25 search ----
    bm25_docs = bm25_search(query, top_k)

    # ---- Combine results ----
    combined = dense_docs + bm25_docs

    # Lower score = better for dense → convert to a unified ranking
    for doc in combined:
        doc["rank_score"] = float(doc["score"])

    # Sort best → worst
    combined = sorted(combined, key=lambda x: x["rank_score"])

    return combined[:top_k]
