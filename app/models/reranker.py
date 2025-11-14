from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import torch
from torch import nn

from langchain_core.documents import Document


def build_reranker_net(embedding_dim: int) -> nn.Module:
    input_dim = embedding_dim * 3
    return nn.Sequential(
        nn.Linear(input_dim, 256),
        nn.ReLU(),
        nn.Linear(256, 1),
    )


def _make_features(q: np.ndarray, d: np.ndarray) -> np.ndarray:
    return np.concatenate([q, d, q * d], axis=-1)


@dataclass
class Reranker:
    embedding_model: any
    model: nn.Module
    device: str = "cpu"

    @classmethod
    def from_pretrained(cls, embedding_model, model_path: str, device: str = "cpu"):
        sample_vec = embedding_model.embed_query("hello")
        emb_dim = len(sample_vec)

        model = build_reranker_net(emb_dim)
        state = torch.load(model_path, map_location=device)
        model.load_state_dict(state)
        model.to(device)
        model.eval()

        return cls(embedding_model=embedding_model, model=model, device=device)

    def score_docs(self, query: str, docs: List[Document]) -> List[Tuple[Document, float]]:
        q_emb = np.array(self.embedding_model.embed_query(query))
        doc_texts = [d.page_content for d in docs]
        doc_embs = np.array(self.embedding_model.embed_documents(doc_texts))

        features = np.stack(
            [_make_features(q_emb, doc_embs[i]) for i in range(len(docs))],
            axis=0
        )

        with torch.no_grad():
            x = torch.tensor(features, dtype=torch.float32, device=self.device)
            scores = self.model(x).squeeze(-1).cpu().numpy().tolist()

        return list(zip(docs, scores))

    def rerank(
        self,
        query: str,
        docs: List[Document],
        top_k: Optional[int] = None
    ) -> List[Document]:

        top_k = top_k or len(docs)
        scored = self.score_docs(query, docs)
        scored.sort(key=lambda x: x[1], reverse=True)
        return [d for d, _ in scored[:top_k]]
