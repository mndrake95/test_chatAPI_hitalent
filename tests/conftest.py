import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio

from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.database import get_db, Base
from app.config import settings
from app.main import app


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/test_db"

engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(bind=engine_test, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    await asyncio.sleep(1)
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield  
    
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def session():
    async with engine_test.connect() as connection:
        async with connection.begin() as transaction:
            async with TestingSessionLocal(bind=connection) as session:
                yield session
            await transaction.rollback()

@pytest.fixture(scope="function", autouse=True)
async def client(session):
    async def _get_test_db():
        yield session
    app.dependency_overrides[get_db] = _get_test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
        app.dependency_overrides.clear()

