# app/rag/reranker.py

"""
Bank-grade neural reranker using a Cross-Encoder.

This implementation:
- Reranks top candidates using MiniLM Cross Encoder
- Provides safe fallback if the model cannot be loaded
- Works offline once downloaded
- Fully compatible with Python 3.9
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch

    HF_AVAILABLE = True

except Exception:
    HF_AVAILABLE = False
    logger.warning("HuggingFace transformers not available. Using fallback reranker.")


# Global model cache
_TOKENIZER = None
_MODEL = None


def _load_model():
    """
    Lazy load the reranker model on first use.
    """
    global _TOKENIZER, _MODEL

    if not HF_AVAILABLE:
        return False

    if _MODEL is not None:
        return True

    try:
        model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"

        _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
        _MODEL = AutoModelForSequenceClassification.from_pretrained(model_name)

        logger.info("Loaded Cross-Encoder reranker model.")
        return True

    except Exception as e:
        logger.error(f"Could not load cross-encoder model: {e}")
        return False


def cross_encoder_rerank(query: str, candidates: List[Dict]) -> List[Dict]:
    """
    Reranks candidate documents based on semantic relevance.

    candidates format:
    [
        { "content": "...", "score": float },
        ...
    ]

    Output is sorted high → low relevance.
    """

    # Fallback: return dense+bm25 scores unchanged
    if not _load_model():
        logger.warning("Cross-encoder unavailable. Using fallback ranking.")
        return sorted(candidates, key=lambda x: x["score"], reverse=True)

    # Use Torch for scoring
    rerank_inputs = [
        (query, c["content"]) for c in candidates
    ]

    scores = []

    for q, d in rerank_inputs:
        inputs = _TOKENIZER(
            q,
            d,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            output = _MODEL(**inputs)
            score = float(output.logits[0].item())

        scores.append(score)

    # Attach new scores
    reranked = []
    for item, new_score in zip(candidates, scores):
        reranked.append({
            "content": item["content"],
            "score": new_score,
            "source": item.get("source", "rerank")
        })

    # Sort by cross-encoder score
    reranked = sorted(reranked, key=lambda x: x["score"], reverse=True)

    return reranked
