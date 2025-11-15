import math
from backend.vectorstore import collection


# BM25 parameters
k1 = 1.5
b = 0.75


def tokenize(text: str):
    return text.lower().split()


def compute_idf(corpus_tokens):
    """
    Compute IDF for each unique term in the corpus.
    """
    N = len(corpus_tokens)
    df = {}

    for tokens in corpus_tokens:
        unique_terms = set(tokens)
        for term in unique_terms:
            df[term] = df.get(term, 0) + 1

    idf = {}
    for term, freq in df.items():
        idf[term] = math.log(1 + (N - freq + 0.5) / (freq + 0.5))

    return idf


def bm25_search(query: str, top_k: int = 5):
    """
    BM25 lexical search over Chroma's stored documents.
    Returns list of dicts with text + score.
    """

    # ---- Fetch ALL documents from Chroma ----
    all_docs = collection.get()
    documents = all_docs["documents"]
    metadatas = all_docs["metadatas"]

    if not documents:
        return []

    # ---- Tokenize corpus ----
    corpus_tokens = [tokenize(doc) for doc in documents]

    # ---- Tokenize query ----
    query_tokens = tokenize(query)

    # ---- Compute IDF ----
    idf = compute_idf(corpus_tokens)

    # ---- BM25 scoring ----
    avgdl = sum(len(doc) for doc in corpus_tokens) / len(corpus_tokens)
    scores = []

    for idx, doc_tokens in enumerate(corpus_tokens):
        score = 0
        doc_len = len(doc_tokens)
        tf_counts = {}

        for token in doc_tokens:
            tf_counts[token] = tf_counts.get(token, 0) + 1

        for q in query_tokens:
            if q not in tf_counts:
                continue

            tf = tf_counts[q]
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / avgdl))
            score += idf.get(q, 0) * (numerator / denominator)

        scores.append((idx, score))

    # ---- Sort best → worst ----
    scores.sort(key=lambda x: x[1], reverse=True)
    top_scores = scores[:top_k]

    # ---- Convert back into RAG doc format ----
    results = []
    for idx, score in top_scores:
        results.append({
            "text": documents[idx],
            "score": float(-score),  # negative so lower = better
            "source": metadatas[idx]["source"],
            "page": metadatas[idx]["page"],
            "chunk_index": idx
        })

    return results
