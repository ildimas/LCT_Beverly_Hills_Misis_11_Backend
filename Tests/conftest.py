import asyncio
import os
from datetime import timedelta
from typing import Any
from typing import Generator
import asyncpg
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from sqlalchemy.sql import text
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from API.App.core.db import get_db
from API.App.api.main import app

SQLALCHEMY_TEST_DATABASE_URL = f'postgresql+asyncpg://test:washingtonsilver@localhost:5433/main_test_db'

CLEAN_TABLES = [
    "users",
]

@pytest.fixture(scope="session")
def event_loop_policy():
    policy = asyncio.get_event_loop_policy()
    old_policy = asyncio.get_event_loop_policy()
    asyncio.set_event_loop_policy(policy)
    yield policy
    asyncio.set_event_loop_policy(old_policy)


@pytest.fixture(scope="session", autouse=True)
async def run_migrations():
    os.system("alembic init migrations")
    os.system('alembic revision --autogenerate -m "test running migrations"')
    os.system("alembic upgrade heads")


@pytest.fixture(scope="session")
async def async_session_test():
    engine = create_async_engine(SQLALCHEMY_TEST_DATABASE_URL, future=True, echo=True)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(async_session_test):
    """Clean data in all tables before running test function"""
    async with async_session_test() as session:
        async with session.begin():
            for table_for_cleaning in CLEAN_TABLES:
                await session.execute(text(f"TRUNCATE TABLE {table_for_cleaning};"))

async def _get_test_db():
    try:
        # create async engine for interaction with database
        test_engine = create_async_engine(
            SQLALCHEMY_TEST_DATABASE_URL, future=True, echo=True
        )

        # create session for the interaction with database
        test_async_session = sessionmaker(
            test_engine, expire_on_commit=False, class_=AsyncSession
        )
        yield test_async_session()
    finally:
        pass




@pytest.fixture(scope="function")
async def client() -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client
        
@pytest.fixture(scope="session")
async def asyncpg_pool():
    pool = await asyncpg.create_pool(
        "".join(SQLALCHEMY_TEST_DATABASE_URL.split("+asyncpg")))
    yield pool
    await pool.close()
    
    
@pytest.fixture
async def get_user_from_database(asyncpg_pool):
    async def get_user_from_database_by_uuid(user_id: str):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetch(
                """SELECT * FROM users WHERE user_id = $1;""", user_id
            )

    return get_user_from_database_by_uuid

