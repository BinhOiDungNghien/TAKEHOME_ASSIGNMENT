from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import QueuePool
from typing import AsyncGenerator
from app.core.config import settings

# 1. Create a global, shared Async Engine with a connection pool
# QueuePool is the default for create_async_engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,          # Maintain up to 20 permanent connections
    max_overflow=10,       # Allow 10 extra connections during spikes
    pool_timeout=30,       # Timeout after 30s of waiting for a connection
    pool_recycle=1800,     # Reset connections every 30 mins to avoid staleness
    pool_pre_ping=True,    # Check connection health before using
    echo=False,
    future=True
)

# 2. Create a shared session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# For FastAPI dependency injection
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session from the global connection pool."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Note: We no longer need engine.dispose() in get_db because the engine 
# is shared across the entire application lifecycle.
