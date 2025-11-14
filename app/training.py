from typing import Optional, List, Dict
import json
import os
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from .config import settings
from .embeddings import get_embedding_model
from .models.reranker import build_reranker_net, _make_features


class RerankDataset(Dataset):
    def __init__(self, samples: List[Dict], embedding_model):
        self.samples = samples
        self.embedding_model = embedding_model

        self.emb_dim = len(self.embedding_model.embed_query("hello"))
        self._features_pos, self._features_neg = self._build_features()

    def _build_features(self):
        pos_feats = []
        neg_feats = []

        for s in self.samples:
            q = s["query"]
            pos = s["positive"]
            neg = s["negative"]

            q_emb = np.array(self.embedding_model.embed_query(q))
            pos_emb = np.array(self.embedding_model.embed_documents([pos])[0])
            neg_emb = np.array(self.embedding_model.embed_documents([neg])[0])

            pos_feats.append(_make_features(q_emb, pos_emb))
            neg_feats.append(_make_features(q_emb, neg_emb))

        return np.array(pos_feats), np.array(neg_feats)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return (
            self._features_pos[idx].astype(np.float32),
            self._features_neg[idx].astype(np.float32),
        )


def load_training_samples(path: str) -> List[Dict]:
    if not os.path.exists(path):
        print(f"WARNING: {path} missing — using demo data.")
        return [
            {
                "query": "What is RAG?",
                "positive": "RAG is Retrieval-Augmented Generation.",
                "negative": "RAG is a type of sandwich."
            },
            {
                "query": "What is backpropagation?",
                "positive": "It computes gradients using the chain rule.",
                "negative": "Backpropagation is a fitness technique."
            }
        ]

    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def train_reranker(
    jsonl_path: Optional[str] = None,
    num_epochs: int = 5,
    batch_size: int = 8,
    lr: float = 1e-3,
):

    os.makedirs(settings.training_dir, exist_ok=True)
    jsonl_path = jsonl_path or os.path.join(settings.training_dir, "training_data.jsonl")

    embedding_model = get_embedding_model()
    samples = load_training_samples(jsonl_path)

    dataset = RerankDataset(samples, embedding_model)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    device = "cpu"
    model = build_reranker_net(dataset.emb_dim).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MarginRankingLoss(margin=0.1)

    model.train()

    for epoch in range(num_epochs):
        total_loss = 0.0

        for pos_feats, neg_feats in loader:
            pos_feats = pos_feats.to(device)
            neg_feats = neg_feats.to(device)

            pos_scores = model(pos_feats).squeeze(-1)
            neg_scores = model(neg_feats).squeeze(-1)
            target = torch.ones_like(pos_scores)

            loss = criterion(pos_scores, neg_scores, target)

            optimizer.zero_grad()
            loss.backward()   # BACKPROP
            optimizer.step()

            total_loss += loss.item() * pos_feats.size(0)

        avg_loss = total_loss / len(dataset)
        print(f"Epoch {epoch+1}/{num_epochs} — Loss: {avg_loss:.4f}")

    torch.save(model.state_dict(), settings.reranker_model_path)
    print(f"Saved model to {settings.reranker_model_path}")


if __name__ == "__main__":
    train_reranker()
