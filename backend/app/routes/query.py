from typing import Annotated

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.services.llm import generate_answer
from app.services.retriever import retrieve_chunks


router = APIRouter(tags=["research"])


class QueryRequest(BaseModel):
    question: Annotated[str, Field(min_length=3, max_length=2000)]
    document_id: str | None = None
    top_k: Annotated[int, Field(ge=1, le=10)] | None = None


@router.post("/query")
async def query_document(request: QueryRequest):
    try:
        chunks = retrieve_chunks(
            request.question,
            request.top_k or settings.top_k,
            request.document_id,
        )

        if not chunks:
            return {
                "question": request.question,
                "answer": "I could not find relevant evidence in the indexed research papers.",
                "sources": [],
            }

        answer = generate_answer(request.question, chunks)
        sources = [
            {
                "source": i,
                "document_id": item["metadata"].get("document_id"),
                "filename": item["metadata"].get("filename"),
                "page": item["metadata"].get("page"),
                "chunk_id": (
                    f"{item['metadata'].get('document_id')}_"
                    f"p{item['metadata'].get('page')}_"
                    f"c{item['metadata'].get('chunk_index')}"
                ),
                "distance": item.get("distance"),
            }
            for i, item in enumerate(chunks, 1)
        ]

        return {"question": request.question, "answer": answer, "sources": sources}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to answer the question: {exc}") from exc
