from sqlalchemy import Column, Integer, String
# from core.db import Base
# from core.db import engine
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import Boolean
from sqlalchemy.orm import declarative_base
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import engine
import asyncio

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)

# async def init_models():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)

# init_models()