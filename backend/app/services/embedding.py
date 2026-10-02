from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def generate_embeddings(chunks: list[str]):
    if not chunks:
        return []
    return get_embedding_model().encode(chunks, normalize_embeddings=True)
