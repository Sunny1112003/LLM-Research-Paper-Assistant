from app.config import settings
from app.services.embedding import get_embedding_model
from app.services.vector_store import collection


def retrieve_chunks(query: str, n_results: int | None = None,
                    document_id: str | None = None) -> list[dict]:
    if not query.strip():
        return []

    top_k = max(1, min(n_results or settings.top_k, 10))
    embedding = get_embedding_model().encode(
        query, normalize_embeddings=True
    ).tolist()

    kwargs = {
        "query_embeddings": [embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if document_id:
        kwargs["where"] = {"document_id": document_id}

    result = collection.query(**kwargs)
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    return [
        {"text": d, "metadata": m or {}, "distance": dist}
        for d, m, dist in zip(documents, metadatas, distances)
    ]
