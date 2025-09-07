from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from core.settings import settings
from db.models import Base

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db() -> None:
    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        except Exception:
            pass
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))
        except Exception:
            pass
        await conn.run_sync(Base.metadata.create_all)
