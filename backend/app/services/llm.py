import ollama

from app.config import settings


def _format_context(chunks: list[dict]) -> str:
    return "\n\n".join(f"[SOURCE {i}] {x['metadata'].get('filename', 'Unknown document')}, page {x['metadata'].get('page', '?')}\n{x['text']}" for i, x in enumerate(chunks, 1)) or "No relevant source passages were retrieved."


def generate_answer(question: str, retrieved_chunks: list[dict], history: list[tuple[str, str]] | None = None) -> str:
    history_text = "\n".join(f"{role.upper()}: {content}" for role, content in (history or [])[-10:])
    prompt = f"""You are a research paper intelligence assistant.
Answer only from the supplied source passages. Use conversation history only to resolve references such as 'it', 'this method', or 'the previous paper'.
Rules:
- Do not invent unsupported facts.
- If evidence is insufficient, say so clearly.
- Cite factual claims inline as [SOURCE N].
- If sources disagree, describe the disagreement.
- Be precise and concise.

CONVERSATION HISTORY:
{history_text or 'None'}

SOURCE PASSAGES:
{_format_context(retrieved_chunks)}

QUESTION:
{question}

ANSWER:
"""
    response = ollama.chat(model=settings.ollama_model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()
