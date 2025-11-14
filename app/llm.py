# app/llm.py

"""
Bank-grade LLM answer generator with:
- secure prompting
- context isolation
- audit-friendly structure
- deterministic formatting
- OpenAI / LangChain v0.2+ support
"""

from typing import Optional
from langchain_openai import ChatOpenAI

# --------------------------------------------------------------------
# 1. Load model (replace with AzureOpenAI if needed)
# --------------------------------------------------------------------

def _load_llm() -> ChatOpenAI:
    """
    Load model using LangChain v0.2+ compatible API.
    You may replace with gpt-4o-mini or Azure endpoints.
    """
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=600,
    )

# --------------------------------------------------------------------
# 2. Build secure, audit-grade prompt
# --------------------------------------------------------------------

SYSTEM_PROMPT = """
You are a regulated-industry assistant (bank/finance). 
You MUST:
- Use ONLY the provided context.
- Explicitly state when information is not present in the context.
- Do NOT hallucinate.
- Follow compliance: clear, factual, short answers.
- Include a one-line “Source Summary” referencing the chunks used.
"""

USER_PROMPT_TEMPLATE = """
User question:
{query}

Relevant retrieved context:
--------------------------------
{context}
--------------------------------

Instructions:
1. Answer ONLY using the provided context.
2. If the context does not contain the answer, say:
   "The provided documents do not contain this information."
3. Keep the answer concise, factual, and compliant.
4. Provide a 1-sentence Source Summary listing which chunks were used.
"""

# --------------------------------------------------------------------
# 3. Main function used by retriever + FastAPI
# --------------------------------------------------------------------

def answer_with_context(query: str, context: str) -> str:
    """
    Generate an LLM answer constrained strictly to retrieved context.
    Required for bank-grade RAG deployments.
    """

    llm = _load_llm()

    # Build final prompt
    prompt = USER_PROMPT_TEMPLATE.format(
        query=query.strip(),
        context=context.strip()
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    # Call model
    response = llm.invoke(messages)

    # LangChain returns AIMessage with .content
    return response.content
