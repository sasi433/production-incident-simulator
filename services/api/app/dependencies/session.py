from fastapi import Cookie, HTTPException, status
import structlog

from app.services.sessions import get_session

log = structlog.get_logger("session_dependency")


async def require_session(session_id: str | None = Cookie(default=None)) -> dict:
    if not session_id:
        log.warning("session_cookie_missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_session",
        )

    session = await get_session(session_id)
    if not session:
        log.warning("session_not_found", session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_session",
        )

    return {"session_id": session_id, **session}