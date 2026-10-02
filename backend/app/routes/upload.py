import hashlib
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.services.embedding import generate_embeddings
from app.services.pdf_reader import read_pdf
from app.services.text_chunker import chunk_pages
from app.services.text_cleaner import clean_text
from app.services.vector_store import document_exists, store_embeddings


router = APIRouter(tags=["documents"])
UPLOAD_FOLDER = Path(settings.upload_dir)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def _safe_filename(filename: str) -> str:
    name = Path(filename or "").name
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
    return name or "document.pdf"


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    filename = _safe_filename(file.filename or "")

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
    if document_exists(file_hash):
        raise HTTPException(409, "This exact PDF has already been indexed.")

    document_id = uuid4().hex
    stored_path = UPLOAD_FOLDER / f"{document_id}_{filename}"

    try:
        stored_path.write_bytes(content)
        pages = read_pdf(str(stored_path))
        cleaned_pages = [
            type(page)(page=page.page, text=clean_text(page.text))
            for page in pages
        ]
        chunks = chunk_pages(cleaned_pages)

        if not chunks:
            raise HTTPException(
                422,
                "The PDF contains no extractable text. Scanned PDFs require OCR.",
            )

        embeddings = generate_embeddings([chunk.text for chunk in chunks])
        store_embeddings(document_id, filename, file_hash, chunks, embeddings)

    except HTTPException:
        stored_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to process PDF: {exc}") from exc

    return {
        "message": "PDF uploaded and indexed successfully",
        "document_id": document_id,
        "filename": filename,
        "file_hash": file_hash,
        "total_pages": len(pages),
        "total_chunks": len(chunks),
    }
