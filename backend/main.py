from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.query import router as query_router
from app.routes.upload import router as upload_router


app = FastAPI(
    title="Research Paper Intelligence Assistant API",
    version="0.2.0",
    description="Page-aware RAG API for grounded research-paper question answering.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(query_router)


@app.get("/")
def root():
    return {"message": "Research Paper Intelligence Assistant API is running", "version": app.version}


@app.get("/health")
def health():
    return {"status": "ok"}
