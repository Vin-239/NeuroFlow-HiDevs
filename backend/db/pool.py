import asyncpg
from config import settings

db_pool = None

async def create_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT
    )

async def close_pool():
    global db_pool
    if db_pool:
        await db_pool.close()