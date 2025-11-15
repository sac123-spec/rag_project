import os
import shutil
import chromadb
from chromadb.config import Settings
from backend.config import VECTOR_DB_DIR, DATA_DIR
from backend.rag.chunking import chunk_pdf

# Create Chroma client using NEW API (post–2024)
client = chromadb.PersistentClient(path=VECTOR_DB_DIR)

collection = client.get_or_create_collection(
    name="rag_docs",
    metadata={"hnsw:space": "cosine"}
)

def list_documents():
    return [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]


def delete_document(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        os.remove(path)


def rebuild_index():
    # Reset database
    shutil.rmtree(VECTOR_DB_DIR, ignore_errors=True)
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    global client, collection
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    collection = client.get_or_create_collection("rag_docs")

    chunk_count = 0
    for pdf in list_documents():
        chunks = chunk_pdf(os.path.join(DATA_DIR, pdf))
        for chunk in chunks:
            collection.add(
                ids=[chunk["id"]],
                documents=[chunk["text"]],
                metadatas=[{"source": chunk["source"], "page": chunk["page"]}]
            )
            chunk_count += 1

    return chunk_count
