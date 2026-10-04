from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Chat, Message, Workspace
from app.schemas import ChatCreate, ChatUpdate, MessageCreate
from app.services.llm import generate_answer
from app.services.retriever import retrieve_chunks

router = APIRouter(tags=["chats"])


def serialize_chat(db: Session, c: Chat) -> dict:
    count = db.scalar(select(func.count(Message.id)).where(Message.chat_id == c.id)) or 0
    return {"id": c.id, "workspace_id": c.workspace_id, "title": c.title, "is_pinned": c.is_pinned, "message_count": count, "created_at": c.created_at}


def serialize_message(m: Message) -> dict:
    return {"id": m.id, "role": m.role, "content": m.content, "sources": m.sources or [], "created_at": m.created_at}


@router.get("/workspaces/{workspace_id}/chats")
def list_chats(workspace_id: str, db: Session = Depends(get_db)):
    if not db.get(Workspace, workspace_id):
        raise HTTPException(404, "Workspace not found.")
    rows = db.scalars(select(Chat).where(Chat.workspace_id == workspace_id).order_by(Chat.is_pinned.desc(), Chat.created_at.desc())).all()
    return {"chats": [serialize_chat(db, c) for c in rows]}


@router.post("/workspaces/{workspace_id}/chats", status_code=201)
def create_chat(workspace_id: str, payload: ChatCreate, db: Session = Depends(get_db)):
    if not db.get(Workspace, workspace_id):
        raise HTTPException(404, "Workspace not found.")
    c = Chat(workspace_id=workspace_id, title=payload.title.strip())
    db.add(c)
    db.commit()
    db.refresh(c)
    return serialize_chat(db, c)


@router.patch("/chats/{chat_id}")
def update_chat(chat_id: str, payload: ChatUpdate, db: Session = Depends(get_db)):
    c = db.get(Chat, chat_id)
    if not c:
        raise HTTPException(404, "Chat not found.")
    if payload.title is not None:
        c.title = payload.title.strip()
    if payload.is_pinned is not None:
        c.is_pinned = payload.is_pinned
    db.commit()
    db.refresh(c)
    return serialize_chat(db, c)


@router.delete("/chats/{chat_id}", status_code=204)
def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    c = db.get(Chat, chat_id)
    if not c:
        raise HTTPException(404, "Chat not found.")
    db.delete(c)
    db.commit()


@router.get("/chats/{chat_id}/messages")
def list_messages(chat_id: str, db: Session = Depends(get_db)):
    if not db.get(Chat, chat_id):
        raise HTTPException(404, "Chat not found.")
    rows = db.scalars(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.asc())).all()
    return {"messages": [serialize_message(m) for m in rows]}


@router.post("/chats/{chat_id}/messages", status_code=201)
def send_message(chat_id: str, payload: MessageCreate, db: Session = Depends(get_db)):
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found.")
    question = payload.question.strip()
    if not question:
        raise HTTPException(422, "Question cannot be empty.")

    history_rows = db.scalars(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at.asc()).limit(20)).all()
    user_message = Message(chat_id=chat_id, role="user", content=question)
    db.add(user_message)
    db.flush()

    chunks = retrieve_chunks(question, payload.top_k, workspace_id=chat.workspace_id, document_ids=payload.document_ids)
    sources = [
        {"source": i, "document_id": x["metadata"].get("document_id"), "filename": x["metadata"].get("filename"), "page": x["metadata"].get("page"), "chunk_id": f'{x["metadata"].get("document_id")}_p{x["metadata"].get("page")}_c{x["metadata"].get("chunk_index")}', "distance": x.get("distance")}
        for i, x in enumerate(chunks, 1)
    ]
    if chunks:
        history = [(m.role, m.content) for m in history_rows]
        answer = generate_answer(question, chunks, history)
    else:
        answer = "I could not find relevant evidence in the indexed papers in this workspace."

    assistant_message = Message(chat_id=chat_id, role="assistant", content=answer, sources=sources)
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    return {"answer": answer, "sources": sources, "message": serialize_message(assistant_message)}
