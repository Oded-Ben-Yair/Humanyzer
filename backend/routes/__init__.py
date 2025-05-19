# Routes package initialization
from fastapi import APIRouter

router = APIRouter(tags=["routes"])

@router.get("/version")
async def get_version():
    """
    Get the current version of the application.
    """
    return {"version": "1.0.0"}
