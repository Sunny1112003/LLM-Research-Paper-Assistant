import hashlib
import re
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Document, Workspace
from app.routes.workspaces import serialize_document
from app.services.embedding import generate_embeddings
from app.services.pdf_reader import read_pdf
from app.services.text_chunker import chunk_pages
from app.services.text_cleaner import clean_text
from app.services.vector_store import store_embeddings

router = APIRouter(tags=["documents"])
UPLOAD_FOLDER = Path(settings.upload_dir)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def safe_filename(filename: str) -> str:
    name = Path(filename or "").name
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
    return name or "document.pdf"


@router.post("/workspaces/{workspace_id}/documents", status_code=201)
async def upload_document(workspace_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not db.get(Workspace, workspace_id):
        raise HTTPException(404, "Workspace not found.")
    filename = safe_filename(file.filename or "")
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    content = await file.read()
    if not content:
        raise HTTPException(400, "The uploaded PDF is empty.")
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(413, f"PDF exceeds the {settings.max_file_size_mb} MB upload limit.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(400, "The uploaded file is not a valid PDF.")

    file_hash = hashlib.sha256(content).hexdigest()
    duplicate = db.scalar(select(Document).where(Document.workspace_id == workspace_id, Document.file_hash == file_hash))
    if duplicate:
        raise HTTPException(409, "This exact PDF is already indexed in this workspace.")

    document = Document(workspace_id=workspace_id, filename=filename, file_hash=file_hash, status="processing", file_size=len(content), stored_path="")
    db.add(document)
    db.commit()
    db.refresh(document)
    stored_path = UPLOAD_FOLDER / f"{document.id}_{filename}"
    document.stored_path = str(stored_path)
    try:
        stored_path.write_bytes(content)
        pages = read_pdf(str(stored_path))
        cleaned = [type(page)(page=page.page, text=clean_text(page.text)) for page in pages]
        chunks = chunk_pages(cleaned)
        if not chunks:
            raise ValueError("The PDF contains no extractable text. Scanned PDFs require OCR.")
        embeddings = generate_embeddings([c.text for c in chunks])
        store_embeddings(document.id, workspace_id, filename, file_hash, chunks, embeddings)
        document.total_pages = len(pages)
        document.total_chunks = len(chunks)
        document.status = "ready"
        db.commit()
    except Exception as exc:
        db.rollback()
        from app.services.vector_store import delete_document_vectors
        delete_document_vectors(document.id)
        stored_path.unlink(missing_ok=True)
        failed = db.get(Document, document.id)
        if failed:
            db.delete(failed)
            db.commit()
        raise HTTPException(500, f"Failed to process PDF: {exc}") from exc
    return serialize_document(document)


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found.")
    from app.services.vector_store import delete_document_vectors
    delete_document_vectors(document.id)
    Path(document.stored_path).unlink(missing_ok=True)
    db.delete(document)
    db.commit()
