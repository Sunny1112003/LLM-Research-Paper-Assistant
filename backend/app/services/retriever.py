from app.config import settings
from app.services.embedding import get_embedding_model
from app.services.vector_store import collection


def retrieve_chunks(query: str, n_results: int | None = None, workspace_id: str | None = None, document_ids: list[str] | None = None) -> list[dict]:
    if not query.strip():
        return []
    top_k = max(1, min(n_results or settings.top_k, 10))
    embedding = get_embedding_model().encode(query, normalize_embeddings=True).tolist()
    filters = []
    if workspace_id:
        filters.append({"workspace_id": workspace_id})
    if document_ids:
        filters.append({"document_id": {"$in": document_ids}})
    where = None
    if len(filters) == 1:
        where = filters[0]
    elif filters:
        where = {"$and": filters}
    kwargs = {"query_embeddings": [embedding], "n_results": top_k, "include": ["documents", "metadatas", "distances"]}
    if where:
        kwargs["where"] = where
    result = collection.query(**kwargs)
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    return [{"text": d, "metadata": m or {}, "distance": dist} for d, m, dist in zip(docs, metas, distances)]
