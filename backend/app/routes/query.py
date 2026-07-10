from fastapi import APIRouter
from pydantic import BaseModel

from app.services.retriever import retrieve_chunks
from app.services.llm import generate_answer

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
async def query_document(request: QueryRequest):
    chunks = retrieve_chunks(request.question)
    answer = generate_answer(request.question, chunks)

    return {
        "question": request.question,
        "answer": answer
    }