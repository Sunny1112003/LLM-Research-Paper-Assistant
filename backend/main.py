from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.chats import router as chats_router
from app.routes.documents import router as documents_router
from app.routes.workspaces import router as workspaces_router


app = FastAPI(
    title="Research Paper Intelligence Assistant API",
    version="1.0.0",
    description="Persistent workspace-based RAG API for research papers.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workspaces_router)
app.include_router(documents_router)
app.include_router(chats_router)


@app.get("/")
def root():
    return {
        "message": "Research Paper Intelligence Assistant API is running",
        "version": app.version,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
