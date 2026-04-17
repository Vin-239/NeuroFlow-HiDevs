import httpx
import redis.asyncio as aioredis
from db.pool import db_pool
from config import settings

async def check_postgres() -> bool:
    if not db_pool:
        return False
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False

async def check_redis() -> bool:
    try:
        redis = aioredis.from_url(
            f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
        )
        await redis.ping()
        await redis.aclose()
        return True
    except Exception:
        return False

async def check_mlflow() -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.MLFLOW_TRACKING_URI, timeout=2.0)
            return response.status_code == 200
    except Exception:
        return False