from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """
    Wrapper around a HuggingFace CrossEncoder for reranking retrieved documents.

    - Lazy-loads the model on first use to avoid heavy startup cost.
    - Safely handles the case where there are no documents (returns [] instead of crashing).
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None  # will be loaded lazily

    def load(self):
        if self.model is None:
            self.model = CrossEncoder(self.model_name)

    def rerank(self, query: str, documents: list) -> list:
        """
        Rerank a list of documents based on relevance to a query.

        Each document is expected to be a dict with at least a "text" field.
        Returns a new list sorted by descending score.
        """

        # If there are no documents, just return an empty list
        if not documents:
            return []

        # Ensure model is loaded
        self.load()

        # Build pairs [query, document_text] for all documents
        pairs = []
        for d in documents:
            text = d.get("text", "")
            pairs.append([query, text])

        # Still guard: if all texts are empty for some reason, skip scoring
        if not pairs:
            return documents

        # Predict relevance scores
        scores = self.model.predict(pairs)

        # Attach scores back to documents
        for i, score in enumerate(scores):
            documents[i]["score"] = float(score)

        # Sort by score descending (higher is better)
        reranked = sorted(documents, key=lambda x: x["score"], reverse=True)
        return reranked
