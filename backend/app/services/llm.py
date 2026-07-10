import ollama


def generate_answer(question: str, context: list):
    prompt = f"""
You are a research paper assistant.

Answer the user's question using only the provided context.

Context:
{' '.join(context)}

Question:
{question}

Answer:
"""

    response = ollama.chat(
        model="gemma3",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]