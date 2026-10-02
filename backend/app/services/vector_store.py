import chromadb

from app.config import settings
from app.services.text_chunker import DocumentChunk


client = chromadb.PersistentClient(path=settings.chroma_path)
collection = client.get_or_create_collection(
    name=settings.chroma_collection,
    metadata={"description": "Page-aware research paper chunks"},
)


def document_exists(file_hash: str) -> bool:
    result = collection.get(where={"file_hash": file_hash}, include=["metadatas"])
    return bool(result.get("ids"))


def store_embeddings(document_id: str, filename: str, file_hash: str,
                     chunks: list[DocumentChunk], embeddings) -> None:
    if not chunks:
        raise ValueError("No extractable text was found in the PDF.")

    ids = [f"{document_id}_p{c.page}_c{c.chunk_index}" for c in chunks]
    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "file_hash": file_hash,
            "page": c.page,
            "chunk_index": c.chunk_index,
        }
        for c in chunks
    ]

    collection.add(
        ids=ids,
        documents=[c.text for c in chunks],
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
    )
