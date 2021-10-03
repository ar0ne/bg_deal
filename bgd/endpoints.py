"""
App endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def index() -> dict:
    """Index endpoint"""
    return {"hello": "world"}
