# app/models/reranker_training.py

"""
Neural Reranker Training Script (Backprop)
Now supports:
- being called from FastAPI
- returning training logs as a string for the UI
"""

import os

# -------------------------------------------------------------
# MacOS stability fixes
# -------------------------------------------------------------
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
import multiprocessing
multiprocessing.set_start_method("spawn", force=True)

from transformers import AutoTokenizer, AutoModelForSequenceClassification


# -------------------------------------------------------------
# 1. Config
# -------------------------------------------------------------

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-2-v2"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "reranker_model")
NUM_EPOCHS = 3
LEARNING_RATE = 2e-5


# -------------------------------------------------------------
# 2. Example Training Data
# -------------------------------------------------------------

TRAIN_DATA = [
    {
        "query": "What is the purpose of this document?",
        "passage": "This policy document describes the internal procedures for handling customer data securely.",
        "label": 1.0,
    },
    {
        "query": "How do we handle customer data?",
        "passage": "The system should reboot when the battery is low.",
        "label": 0.0,
    },
    {
        "query": "What are the security procedures?",
        "passage": "Security procedures include encryption at rest, encryption in transit, and strict access control.",
        "label": 1.0,
    },
    {
        "query": "What are marketing guidelines?",
        "passage": "Security procedures include encryption at rest, encryption in transit, and strict access control.",
        "label": 0.0,
    },
]


# -------------------------------------------------------------
# 3. Training function (returns logs)
# -------------------------------------------------------------

def train_reranker() -> str:

    logs = []
    logs.append("Starting reranker training process...\n")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logs.append(f"Using device: {device}\n")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.to(device)
    model.train()

    criterion = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(NUM_EPOCHS):
        logs.append(f"\nEpoch {epoch+1}/{NUM_EPOCHS}\n")
        epoch_loss = 0.0

        for i, sample in enumerate(TRAIN_DATA):
            query = sample["query"]
            passage = sample["passage"]
            label = torch.tensor([sample["label"]], dtype=torch.float32, device=device)

            inputs = tokenizer(
                query,
                passage,
                truncation=True,
                padding="max_length",
                max_length=128,
                return_tensors="pt",
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}

            optimizer.zero_grad()

            outputs = model(**inputs)
            logits = outputs.logits.view(-1)

            loss = criterion(logits, label)
            loss.backward()
            optimizer.step()

            logs.append(f"  Sample {i+1} loss = {loss.item():.4f}\n")
            epoch_loss += loss.item()

        avg = epoch_loss / len(TRAIN_DATA)
        logs.append(f"Epoch {epoch+1} average loss: {avg:.4f}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    logs.append("\nTraining complete. Fine-tuned model saved.\n")

    return "".join(logs)
