# Legacy endpoint intentionally retained for compatibility. New clients should use /chats/{chat_id}/messages.
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["legacy"])

class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    document_id: str | None = None

@router.post("/query", deprecated=True)
async def legacy_query(_: QueryRequest):
    raise HTTPException(410, "The legacy /query endpoint is retired. Create a chat and use /chats/{chat_id}/messages.")
