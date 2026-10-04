from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ollama_model: str = "gemma3"
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_path: str = "chroma_db"
    chroma_collection: str = "research_papers_v3"
    upload_dir: str = "uploads"
    database_url: str = "sqlite:///./research_assistant.db"
    top_k: int = 5
    max_file_size_mb: int = 25
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
