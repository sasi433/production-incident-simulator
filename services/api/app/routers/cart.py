import json
from fastapi import APIRouter, Request
from app.cache import redis

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("")
async def get_cart(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        return {"cart": []}

    raw = await redis.get(f"cart:{session_id}")
    if not raw:
        return {"cart": []}

    return {"cart": json.loads(raw)}