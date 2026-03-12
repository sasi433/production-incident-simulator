import uuid

from fastapi import APIRouter, Response
import structlog

from app.services.sessions import create_session

router = APIRouter(tags=["auth"])
log = structlog.get_logger("auth")


@router.post("/login")
async def login(response: Response):
    session_id = str(uuid.uuid4())
    user_id = "demo-user"
    username = "demo"

    await create_session(session_id, user_id=user_id, username=username)

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
    )

    log.info("login_succeeded", session_id=session_id, user_id=user_id)

    return {
        "session_id": session_id,
        "user_id": user_id,
        "username": username,
    }