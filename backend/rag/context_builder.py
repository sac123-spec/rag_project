def build_context(chunks):
    return "\n\n".join(
        [f"[Chunk {i}] {chunk['text']}" for i, chunk in enumerate(chunks)]
    )
