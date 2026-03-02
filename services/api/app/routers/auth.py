from fastapi import APIRouter, Response
import uuid

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login(response: Response):
    session_id = str(uuid.uuid4())
    response.set_cookie("session_id", session_id)
    return {"session_id": session_id}