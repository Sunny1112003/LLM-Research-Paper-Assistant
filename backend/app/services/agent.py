import ollama

from app.services.retriever import retrieve_chunks


SYSTEM_PROMPT = """
You are a research assistant agent. Decide when you need to use a tool before answering.
Use retrieve_paper for questions that require information from the indexed research papers.
Use calculator for arithmetic.
After receiving tool results, synthesize a concise answer grounded in those results.
Do not invent facts that are not supported by the tool results.
"""


def retrieve_paper(query: str) -> str:
    chunks = retrieve_chunks(query, n_results=3)
    return "\n\n".join(chunks)


def calculator(expression: str) -> str:
    allowed = set("0123456789+-*/(). %")
    if not expression or any(char not in allowed for char in expression):
        return "Invalid arithmetic expression."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception:
        return "Unable to evaluate expression."


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_paper",
            "description": "Retrieve relevant passages from the indexed research papers.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform basic arithmetic calculations.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
]


TOOL_HANDLERS = {
    "retrieve_paper": retrieve_paper,
    "calculator": calculator,
}


def run_agent(question: str, max_steps: int = 4) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for _ in range(max_steps):
        response = ollama.chat(model="gemma3", messages=messages, tools=TOOLS)
        message = response["message"]
        messages.append(message)

        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            return message.get("content", "")

        for call in tool_calls:
            name = call["function"]["name"]
            arguments = call["function"].get("arguments", {})
            handler = TOOL_HANDLERS.get(name)
            if handler is None:
                result = "Unknown tool."
            else:
                result = handler(**arguments)
            messages.append({
                "role": "tool",
                "content": result,
            })

    return "The agent reached its maximum tool-use steps without completing the request."