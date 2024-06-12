from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://ildimas:washingtonsilver@{os.getenv("DATABASEHOST")}/main_db'

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True, echo=True, execution_options={"isolation_level": "AUTOCOMMIT"},)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> Generator:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()