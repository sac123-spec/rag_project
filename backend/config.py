import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "data"
VECTOR_DB_DIR = "vectorstore"
MODEL_DIR = "models"
RERANKER_DIR = "models/reranker"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
