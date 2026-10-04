# Legacy endpoint intentionally retained for compatibility. New clients should use /workspaces/{workspace_id}/documents.
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["legacy"])

@router.post("/upload", deprecated=True)
async def legacy_upload():
    raise HTTPException(410, "The legacy /upload endpoint is retired. Upload through /workspaces/{workspace_id}/documents.")
