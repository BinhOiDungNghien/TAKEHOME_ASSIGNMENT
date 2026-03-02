from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from app.core.config import settings

# In production, this engine is used. In tests, we might override DATABASE_URL.
# We keep the engine as a lazy-initialized property or global that responds to settings updates.

def get_engine():
    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True
    )

# For FastAPI dependency injection
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    engine = get_engine()
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
    await engine.dispose()

# For background tasks where we need a fresh session
class AsyncSessionLocal:
    def __init__(self):
        self.engine = get_engine()
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
    
    async def __aenter__(self):
        self.session = self.session_factory()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        await self.engine.dispose()
