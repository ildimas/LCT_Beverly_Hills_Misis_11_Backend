from sqlalchemy import Column, Integer, String
from core.db import Base
from core.db import engine

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
User.metadata.create_all(bind=engine)
