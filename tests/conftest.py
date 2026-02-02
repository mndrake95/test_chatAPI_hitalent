import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.database import get_db, Base
from app.config import settings
from app.main import app


TEST_DATABASE_URL = settings.DB_URL

engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(bind=engine_test, expire_on_commit=False)

@pytest.fixture(scope="session")
def anyio_backend():
    """Указываем бэкенд для anyio."""
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def prepare_database(anyio_backend):
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield  
    
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def session(anyio_backend) -> AsyncSession:
    async with engine_test.connect() as connection:
        async with connection.begin() as transaction:
            async with TestingSessionLocal(bind=connection) as session:
                yield session
            await transaction.rollback()

@pytest.fixture(scope="function", autouse=True)
async def client(session: AsyncSession, anyio_backend):
    async def _get_test_db():
        yield session
    app.dependency_overrides[get_db] = _get_test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        app.dependency_overrides.clear()

