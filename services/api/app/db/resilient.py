import os
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.resilience import DependencyUnavailable, maybe_inject_failure, retryable_dependency_call, with_timeout

log = structlog.get_logger("db")

DB_TIMEOUT_S = float(os.getenv("DB_TIMEOUT_S", "0.8"))
DB_STATEMENT_TIMEOUT_MS = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "800"))


@retryable_dependency_call
async def db_ping(session: AsyncSession) -> bool:
    await maybe_inject_failure("db")
    try:
        # statement_timeout per txn
        await with_timeout(
            "db",
            session.execute(text(f"SET LOCAL statement_timeout = {DB_STATEMENT_TIMEOUT_MS}")),
            DB_TIMEOUT_S,
        )
        await with_timeout("db", session.execute(text("SELECT 1")), DB_TIMEOUT_S)
        return True
    except Exception as exc:
        log.warn("db_ping_failed", error=str(exc))
        raise DependencyUnavailable("db_unavailable") from exc