from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Chat, Document, Note, Workspace
from app.schemas import NoteUpdate, WorkspaceCreate, WorkspaceUpdate

router = APIRouter(tags=["workspaces"])


def serialize_workspace(db: Session, w: Workspace) -> dict:
    document_count = db.scalar(select(func.count(Document.id)).where(Document.workspace_id == w.id)) or 0
    chat_count = db.scalar(select(func.count(Chat.id)).where(Chat.workspace_id == w.id)) or 0
    return {"id": w.id, "name": w.name, "is_pinned": w.is_pinned, "document_count": document_count, "chat_count": chat_count, "created_at": w.created_at}


@router.get("/workspaces")
def list_workspaces(db: Session = Depends(get_db)):
    rows = db.scalars(select(Workspace).order_by(Workspace.is_pinned.desc(), Workspace.created_at.desc())).all()
    return {"workspaces": [serialize_workspace(db, w) for w in rows]}


@router.post("/workspaces", status_code=201)
def create_workspace(payload: WorkspaceCreate, db: Session = Depends(get_db)):
    w = Workspace(name=payload.name.strip())
    db.add(w)
    db.commit()
    db.refresh(w)
    return serialize_workspace(db, w)


@router.get("/workspaces/{workspace_id}")
def get_workspace(workspace_id: str, db: Session = Depends(get_db)):
    w = db.get(Workspace, workspace_id)
    if not w:
        raise HTTPException(404, "Workspace not found.")
    return serialize_workspace(db, w)


@router.patch("/workspaces/{workspace_id}")
def update_workspace(workspace_id: str, payload: WorkspaceUpdate, db: Session = Depends(get_db)):
    w = db.get(Workspace, workspace_id)
    if not w:
        raise HTTPException(404, "Workspace not found.")
    if payload.name is not None:
        w.name = payload.name.strip()
    if payload.is_pinned is not None:
        w.is_pinned = payload.is_pinned
    db.commit()
    db.refresh(w)
    return serialize_workspace(db, w)


@router.delete("/workspaces/{workspace_id}", status_code=204)
def delete_workspace(workspace_id: str, db: Session = Depends(get_db)):
    w = db.get(Workspace, workspace_id)
    if not w:
        raise HTTPException(404, "Workspace not found.")
    from app.services.vector_store import delete_workspace_vectors
    delete_workspace_vectors(workspace_id)
    db.delete(w)
    db.commit()


@router.get("/workspaces/{workspace_id}/documents")
def list_documents(workspace_id: str, db: Session = Depends(get_db)):
    if not db.get(Workspace, workspace_id):
        raise HTTPException(404, "Workspace not found.")
    rows = db.scalars(select(Document).where(Document.workspace_id == workspace_id).order_by(Document.created_at.desc())).all()
    return {"documents": [serialize_document(d) for d in rows]}


def serialize_document(d: Document) -> dict:
    return {"id": d.id, "document_id": d.id, "workspace_id": d.workspace_id, "filename": d.filename, "status": d.status, "file_size": d.file_size, "total_pages": d.total_pages, "total_chunks": d.total_chunks, "created_at": d.created_at}


@router.get("/workspaces/{workspace_id}/notes")
def get_note(workspace_id: str, db: Session = Depends(get_db)):
    if not db.get(Workspace, workspace_id):
        raise HTTPException(404, "Workspace not found.")
    note = db.scalar(select(Note).where(Note.workspace_id == workspace_id))
    return {"content": note.content if note else ""}


@router.put("/workspaces/{workspace_id}/notes")
def update_note(workspace_id: str, payload: NoteUpdate, db: Session = Depends(get_db)):
    if not db.get(Workspace, workspace_id):
        raise HTTPException(404, "Workspace not found.")
    note = db.scalar(select(Note).where(Note.workspace_id == workspace_id))
    if note:
        note.content = payload.content
    else:
        note = Note(workspace_id=workspace_id, content=payload.content)
        db.add(note)
    db.commit()
    return {"content": note.content, "updated_at": note.updated_at}


@router.get("/search")
def search(q: str = Query(min_length=1, max_length=200), db: Session = Depends(get_db)):
    term = f"%{q.strip()}%"
    results = []
    for w in db.scalars(select(Workspace).where(Workspace.name.ilike(term))).all():
        results.append({"type": "workspace", "id": w.id, "title": w.name, "workspace_id": w.id, "created_at": w.created_at})
    for c in db.scalars(select(Chat).where(Chat.title.ilike(term))).all():
        results.append({"type": "chat", "id": c.id, "title": c.title, "workspace_id": c.workspace_id, "created_at": c.created_at})
    for d in db.scalars(select(Document).where(Document.filename.ilike(term))).all():
        results.append({"type": "document", "id": d.id, "title": d.filename, "workspace_id": d.workspace_id, "created_at": d.created_at})
    return {"results": results[:50]}
