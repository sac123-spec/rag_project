from sentence_transformers import CrossEncoder
import os
from backend.config import RERANKER_DIR

os.makedirs(RERANKER_DIR, exist_ok=True)


def train_crossencoder(samples, epochs, batch_size):
    model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    train_data = [
        ([s.query, pos], 1)
        for s in samples
        for pos in s.positive_passages
    ] + [
        ([s.query, neg], 0)
        for s in samples
        for neg in s.negative_passages
    ]

    model.fit(train_data, epochs=epochs, batch_size=batch_size)

    save_path = os.path.join(RERANKER_DIR, "latest")
    model.save(save_path)

    return save_path
