from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    is_pinned: bool | None = None


class ChatCreate(BaseModel):
    title: str = Field(default="New Chat", min_length=1, max_length=200)


class ChatUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    is_pinned: bool | None = None


class MessageCreate(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    document_ids: list[str] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=10)


class NoteUpdate(BaseModel):
    content: str = Field(default="", max_length=20000)


class SearchResult(BaseModel):
    type: str
    id: str
    title: str
    workspace_id: str
    created_at: datetime
    extra: dict[str, Any] = Field(default_factory=dict)
