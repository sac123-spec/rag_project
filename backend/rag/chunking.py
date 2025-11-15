import uuid
from pypdf import PdfReader


def chunk_pdf(path: str, chunk_size: int = 400):
    reader = PdfReader(path)
    chunks = []

    all_text = ""
    for page in reader.pages:
        all_text += page.extract_text() + "\n"

    words = all_text.split()
    buffer = []

    for idx, word in enumerate(words):
        buffer.append(word)
        if len(buffer) >= chunk_size:
            chunks.append(" ".join(buffer))
            buffer = []

    if buffer:
        chunks.append(" ".join(buffer))

    return [
        {
            "id": str(uuid.uuid4()),
            "text": c,
            "source": path,
            "page": i
        }
        for i, c in enumerate(chunks)
    ]
