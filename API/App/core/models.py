from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
# from core.db import Base
# from core.db import engine
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import Boolean
from sqlalchemy.orm import relationship, declarative_base
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import engine
import asyncio

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    categories = relationship("Category", back_populates="user", cascade="all, delete, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete="CASCADE"))
    name = Column(String, nullable=False)
    user = relationship("User", back_populates="categories")
    allocations = relationship("Allocation", back_populates="category", cascade="all, delete, delete-orphan")

class Allocation(Base):
    __tablename__ = "allocations"
    alloc_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.category_id', ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    alloc_result_csv = Column(LargeBinary, nullable=True)
    alloc_result_xlsx = Column(LargeBinary, nullable=True)
    category = relationship("Category", back_populates="allocations")
    bills_to_pay = relationship("BillToPay", back_populates="allocation", cascade="all, delete, delete-orphan")
    reference_books = relationship("ReferenceBook", back_populates="allocation", cascade="all, delete, delete-orphan")
    predictions = relationship("Predictions", back_populates="allocation", cascade="all, delete, delete-orphan")

class BillToPay(Base):
    __tablename__ = "bills_to_pay"
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    bill_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alloc_id = Column(UUID(as_uuid=True), ForeignKey('allocations.alloc_id', ondelete="CASCADE"), nullable=False)
    bills_to_pay = Column(LargeBinary, nullable=True)
    allocation = relationship("Allocation", back_populates="bills_to_pay")

class ReferenceBook(Base):
    __tablename__ = "reference_books"
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    ref_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alloc_id = Column(UUID(as_uuid=True), ForeignKey('allocations.alloc_id', ondelete="CASCADE"), nullable=False)
    reference1 = Column(LargeBinary, nullable=True)
    reference2 = Column(LargeBinary, nullable=True)
    reference3 = Column(LargeBinary, nullable=True)
    reference4 = Column(LargeBinary, nullable=True)
    allocation = relationship("Allocation", back_populates="reference_books")

class Predictions(Base):
    __tablename__ = "prediction_files"
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    preds_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    allocation_id = Column(UUID(as_uuid=True), ForeignKey('allocations.alloc_id', ondelete="CASCADE"), nullable=False)
    csv_data = Column(LargeBinary, nullable=False)
    allocation = relationship("Allocation", back_populates="predictions")