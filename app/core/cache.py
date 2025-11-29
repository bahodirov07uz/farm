from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from redis.asyncio import Redis

from app.core.config import settings


_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return _redis_client


@asynccontextmanager
async def lifespan_redis() -> AsyncIterator[None]:
    client = get_redis_client()
    try:
        yield
    finally:
        await client.aclose()
        global _redis_client
        _redis_client = None












