from fastapi import Request
from propan import apply_types
from propan.annotations import ContextRepo
from starlette.middleware.base import BaseHTTPMiddleware

from core.models import get_contextual_session


class DBSessionMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        @apply_types
        async def with_session_scope(context: ContextRepo):
            async with get_contextual_session() as session:
                with context.scope("session", session):
                    response = await call_next(request)
                    try:
                        await session.commit()
                    except Exception as e:
                        await session.rollback()
                        raise e
                    return response

        return await with_session_scope()
