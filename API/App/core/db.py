from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os 
from dotenv import load_dotenv
load_dotenv()

SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://ildimas:@localhost:5432/main_db' #{os.getenv("DATABASEHOST")}
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
