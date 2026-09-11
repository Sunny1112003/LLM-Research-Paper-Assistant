from fastapi import APIRouter
from pydantic import BaseModel

from app.services.agent import run_agent

router = APIRouter(prefix="/agent")


class AgentRequest(BaseModel):
    question: str


@router.post("/query")
async def agent_query(request: AgentRequest):
    return {
        "question": request.question,
        "answer": run_agent(request.question),
    }