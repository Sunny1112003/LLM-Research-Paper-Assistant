import chromadb

from app.config import settings
from app.services.text_chunker import DocumentChunk

client = chromadb.PersistentClient(path=settings.chroma_path)
collection = client.get_or_create_collection(
    name=settings.chroma_collection,
    metadata={"description": "Workspace-scoped page-aware research paper chunks"},
)


def store_embeddings(document_id: str, workspace_id: str, filename: str, file_hash: str, chunks: list[DocumentChunk], embeddings) -> None:
    if not chunks:
        raise ValueError("No extractable text was found in the PDF.")
    ids = [f"{document_id}_p{c.page}_c{c.chunk_index}" for c in chunks]
    metadatas = [{"document_id": document_id, "workspace_id": workspace_id, "filename": filename, "file_hash": file_hash, "page": c.page, "chunk_index": c.chunk_index} for c in chunks]
    collection.add(ids=ids, documents=[c.text for c in chunks], embeddings=embeddings.tolist(), metadatas=metadatas)


def delete_document_vectors(document_id: str) -> None:
    collection.delete(where={"document_id": document_id})


def delete_workspace_vectors(workspace_id: str) -> None:
    collection.delete(where={"workspace_id": workspace_id})
