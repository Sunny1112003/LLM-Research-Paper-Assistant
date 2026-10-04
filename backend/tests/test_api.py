import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_research_assistant.db"
os.environ["CHROMA_PATH"] = "./test_chroma_db"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_workspace_and_chat_lifecycle():
    created = client.post("/workspaces", json={"name": "Test Workspace"})
    assert created.status_code == 201
    workspace = created.json()

    listed = client.get("/workspaces")
    assert listed.status_code == 200
    assert any(item["id"] == workspace["id"] for item in listed.json()["workspaces"])

    chat = client.post(f"/workspaces/{workspace['id']}/chats", json={"title": "Test Chat"})
    assert chat.status_code == 201
    chat_id = chat.json()["id"]

    messages = client.get(f"/chats/{chat_id}/messages")
    assert messages.status_code == 200
    assert messages.json()["messages"] == []

    notes = client.put(f"/workspaces/{workspace['id']}/notes", json={"content": "Important note"})
    assert notes.status_code == 200
    assert notes.json()["content"] == "Important note"

    deleted = client.delete(f"/workspaces/{workspace['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/workspaces/{workspace['id']}").status_code == 404
