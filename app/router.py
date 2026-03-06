"""Custom API routes for Pal."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ContextReloadRequest(BaseModel):
    recreate: bool = False


@router.post("/context/reload")
def reload_context(body: ContextReloadRequest = ContextReloadRequest()):
    """Re-index context files into pal_knowledge."""
    from context.load_context import load_context

    loaded = load_context(recreate=body.recreate)
    return {"loaded": loaded, "recreate": body.recreate}
