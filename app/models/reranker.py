# app/rag/reranker.py

"""
Runtime neural reranker for your RAG system.

Features:
- Loads your fine-tuned model from app/models/reranker_model/
- Falls back to pre-trained lightweight model if fine-tuned version does not exist
- Provides a clean cross_encoder_rerank() function used in retrieval
"""

import os
import torch
from typing import List, Tuple

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langchain.schema import Document


# ------------------------------------------------------------
# Model paths
# ------------------------------------------------------------

# Fine-tuned model directory
FINE_TUNED_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "models", "reranker_model"
)

# Fallback model
FALLBACK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-2-v2"


# ------------------------------------------------------------
# Load reranker model
# ------------------------------------------------------------

def load_reranker():
    """
    Loads the fine-tuned reranker if available.
    Otherwise loads a default pre-trained model.
    """

    if os.path.exists(FINE_TUNED_MODEL_DIR):
        print("🔹 Loading fine-tuned reranker model...")
        tokenizer = AutoTokenizer.from_pretrained(FINE_TUNED_MODEL_DIR)
        model = AutoModelForSequenceClassification.from_pretrained(FINE_TUNED_MODEL_DIR)
    else:
        print("⚠️ Fine-tuned reranker not found. Using fallback model:", FALLBACK_MODEL_NAME)
        tokenizer = AutoTokenizer.from_pretrained(FALLBACK_MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(FALLBACK_MODEL_NAME)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    return tokenizer, model, device


# Load once on module import
TOKENIZER, MODEL, DEVICE = load_reranker()


# ------------------------------------------------------------
# Reranking function
# ------------------------------------------------------------

def cross_encoder_rerank(query: str, docs: List[Document], top_k: int = 5) -> List[Tuple[Document, float]]:
    """
    Reranks retrieved documents using the cross-encoder model.
    Returns: list of (document, score) sorted descending.
    """

    if not docs:
        return []

    scored_docs = []

    for doc in docs:
        text = doc.page_content

        inputs = TOKENIZER(
            query,
            text,
            truncation=True,
            padding="max_length",
            max_length=128,
            return_tensors="pt",
        ).to(DEVICE)

        with torch.no_grad():
            logits = MODEL(**inputs).logits
            score = float(logits.squeeze().cpu().item())

        scored_docs.append((doc, score))

    # Sort by score descending
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    return scored_docs[:top_k]
