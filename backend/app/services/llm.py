import ollama

from app.config import settings


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant source passages were retrieved."

    return "\n\n".join(
        f"[SOURCE {i}] {item['metadata'].get('filename', 'Unknown document')}, "
        f"page {item['metadata'].get('page', '?')}\n{item['text']}"
        for i, item in enumerate(chunks, 1)
    )


def generate_answer(question: str, retrieved_chunks: list[dict]) -> str:
    prompt = f"""
You are a research paper intelligence assistant.

Answer ONLY from the supplied source passages.

Rules:
- Do not invent unsupported facts.
- If evidence is insufficient, say so clearly.
- Cite factual claims inline as [SOURCE N].
- If sources disagree, describe the disagreement.
- Be precise and concise.

SOURCE PASSAGES:
{_format_context(retrieved_chunks)}

QUESTION:
{question}

ANSWER:
"""
    response = ollama.chat(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()
