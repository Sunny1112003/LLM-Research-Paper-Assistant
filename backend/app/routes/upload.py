from fastapi import APIRouter, UploadFile, File
import shutil
from pathlib import Path

from app.services.pdf_reader import read_pdf
from app.services.text_cleaner import clean_text
from app.services.text_chunker import chunk_text
from app.services.embedding import generate_embeddings
from app.services.vector_store import store_embeddings

router = APIRouter()

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = UPLOAD_FOLDER / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = read_pdf(str(file_path))
    cleaned_text = clean_text(extracted_text)
    chunks = chunk_text(cleaned_text)
    embeddings = generate_embeddings(chunks)

    store_embeddings(chunks, embeddings)

    return {
        "message": "PDF uploaded and indexed successfully",
        "filename": file.filename,
        "total_chunks": len(chunks)
    }