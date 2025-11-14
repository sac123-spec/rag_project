from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from .config import settings


def get_chat_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_chat_model,
        api_key=settings.openai_api_key,
        temperature=0.0,
    )


def format_docs(docs: List[Document]) -> str:
    parts = []
    for i, d in enumerate(docs, start=1):
        parts.append(
            f"[Chunk {i} | Source: {d.metadata.get('source')}] \n{d.page_content}\n"
        )
    return "\n\n".join(parts)


def generate_answer(question: str, context_docs: List[Document]) -> str:
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_template(
        """
You are a helpful assistant answering questions using the provided context.
If the answer is not in the context, say you don't know and do NOT hallucinate.

Context:
{context}

Question:
{question}

Answer in clear, concise language and, when useful, reference the sources by their chunk number.
"""
    )

    context_text = format_docs(context_docs)
    chain = prompt | llm
    response = chain.invoke({"context": context_text, "question": question})
    return response.content
