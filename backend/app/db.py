"""
Async PostgreSQL database connection for Supabase.

Why async?
- Non-blocking: Server can handle other requests while waiting for DB
- Better performance under load
- Required for Supabase connection pooling

Why NullPool?
- Supabase uses Supavisor (their connection pooler) on port 6543
- We let Supabase handle pooling, not SQLAlchemy
- Prevents "too many connections" errors
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager

from app.config import settings


# Create async engine for PostgreSQL
# NullPool: Let Supabase handle connection pooling
engine = create_async_engine(
    settings.SUPABASE_DB_URL,
    poolclass=NullPool,
    # Supabase Supavisor requires these settings
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
    },
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Session factory for creating database sessions
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
)


@asynccontextmanager
async def get_db():
    """
    Context manager for database sessions.

    Usage:
        async with get_db() as db:
            result = await db.execute(query)
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db_session():
    """
    FastAPI dependency for database sessions.

    Usage in routes:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            result = await db.execute(query)
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
