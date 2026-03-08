from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict

from dotenv import load_dotenv
from groq import Groq


# Define project root relative to this file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")  # Load GROQ_API_KEY and GROQ_MODEL from .env at project root


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set in the environment or .env file.")
    return Groq(api_key=api_key)


def _get_model_name() -> str:
    return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def build_system_prompt() -> str:
    """
    System-level instructions for the Groq LLM.

    Enforces:
    - Retrieval-grounded behavior (only use provided context).
    - No investment advice or recommendations.
    - No handling of personal information.
    - Always include at least one source URL in the answer.
    """
    return (
        "You are a factual assistant for Groww HDFC mutual fund schemes.\n"
        "You MUST follow these rules:\n"
        "1. Prioritize answering using the context sections provided to you.\n"
        "2. If the context does not contain the specific answer but you have general knowledge "
        "   about the Groww platform or standard financial terms (like 'expense ratio', 'exit load', etc.), "
        "   you may use that knowledge to provide a helpful, factual answer.\n"
        "3. Always clearly state if you are using general knowledge vs. information from the Groww pages.\n"
        "4. Do NOT provide specific investment advice, recommendations, or personalized comparisons.\n"
        "5. Do NOT handle or respond to personal information questions (PAN, Aadhaar, etc.).\n"
        "6. If you use provided context, include the source URL provided in that context.\n"
        "Always answer in a concise, factual tone, and append a short disclaimer like "
        "'This is general information and is not personalized investment advice.'"
    )


def build_context_block(context_chunks: List[Dict[str, str]]) -> str:
    """
    Build a readable context block for the LLM from retrieved chunks.
    """
    parts = []
    for i, chunk in enumerate(context_chunks, start=1):
        header = (
            f"[Chunk {i} | Scheme: {chunk['scheme_name']} | "
            f"Section: {chunk['attribute_type']} | Source: {chunk['source_url']}]"
        )
        parts.append(header)
        parts.append(chunk["text"])
        parts.append("")  # blank line between chunks
    return "\n".join(parts).strip()


def generate_answer_with_groq(user_query: str, context_chunks: List[Dict[str, str]]) -> str:
    """
    Call the Groq chat completion API with the given query and context.
    """
    if not context_chunks:
        # Upstream code should normally avoid calling us with no context,
        # but we add a defensive guard here as well.
        return (
            "I cannot answer this question from the available information. "
            "Please check the official Groww scheme pages for the latest details."
        )

    client = _get_client()
    model = _get_model_name()

    context_block = build_context_block(context_chunks)

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(),
        },
        {
            "role": "user",
            "content": (
                "User question:\n"
                f"{user_query}\n\n"
                "Context from official Groww pages (use ONLY this information):\n"
                f"{context_block}"
            ),
        },
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
    )

    # Groq client returns choices similar to OpenAI's API.
    return response.choices[0].message.content.strip()


__all__ = ["generate_answer_with_groq"]

