from typing import Union, List, Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from fastapi import  HTTPException
from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
# from core.db import async_session
from models import User, Category, Allocation, ReferenceBook, BillToPay

from logging.config import dictConfig
import logging
from API.App.core.loging_config import LogConfig
dictConfig(LogConfig().model_dump())
logger = logging.getLogger("washingtonsilver")

class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, email: str, password: str) -> User:
        new_user = User(email=email,password=password)
        self.db_session.add(new_user)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = delete(User).where(User.user_id == user_id).returning(User.user_id)
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row:
            await self.db_session.commit()  
            return deleted_user_id_row[0]
        else:
            await self.db_session.rollback()  # Rollback in case of failure
            return None 

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]
        
    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]
        
class CategoryDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def show_all_categories(self, user_id: UUID) -> List[Category]:
        query = select(Category).where(Category.user_id == user_id)
        result = await self.db_session.execute(query)
        categories = result.scalars().all()
        return categories

    async def create_category(self, name: str, user_id: UUID) -> Category:
        existing_category_query = select(Category).where(
            and_(Category.name == name,
            Category.user_id == user_id
        ))
        result = await self.db_session.execute(existing_category_query)
        existing_category = result.scalars().first()
        if existing_category:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        
        new_category = Category(name=name, user_id=user_id)
        self.db_session.add(new_category)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_category
    
    async def delete_category(self, category_name: str, user_id: UUID) -> Union[UUID, None]:
        query = delete(Category).where(
            and_(Category.user_id == user_id, Category.name == category_name)
            ).returning(Category.category_id)
        res = await self.db_session.execute(query)
        deleted_category_row = res.fetchone()
        if deleted_category_row:
            await self.db_session.commit()  
            return deleted_category_row[0]
        else:
            await self.db_session.rollback()  # Rollback in case of failure
            return None 

class AllocationDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def show_all_allocations(self, user_id: UUID, category: Optional[str] = None) -> List[Allocation]:
        query = select(Allocation).where(Allocation.user_id == user_id)
        if category:
            category_uuid = await self._get_category_by_name(category, user_id)
            query = select(Allocation).where(and_(Allocation.user_id == user_id, Allocation.category_id == category_uuid))
        result = await self.db_session.execute(query)
        allocations = result.scalars().all()
        return allocations
        
    async def create_allocation(self, name : str, category_name : str, user_id: UUID) -> Allocation:
        category_uuid = await self._get_category_by_name(category_name, user_id)
        existing_allocation_query = select(Category).where(
            and_(Allocation.name == name,
            Allocation.user_id == user_id,
            Allocation.category_id == category_uuid,
        ))
        result = await self.db_session.execute(existing_allocation_query)
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Allocation with this name and this category already exists")
        new_allocation = Allocation(name=name, category_id=category_uuid, user_id=user_id)
        self.db_session.add(new_allocation)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_allocation
    
    async def _get_category_by_name(self, name: str, user_id : UUID) -> Union[UUID, None]:
        query = select(Category).where(
            and_(Category.name == name, Category.user_id == user_id))
        res = await self.db_session.execute(query)
        category = res.scalars().first()
        try:
            return category.category_id
        except Exception:
            return None
        
    async def delete_allocation(self, allocation_name: str, category_name: str, user_id: UUID) -> Union[UUID, None]:
        query = delete(Allocation).where(
            and_(Allocation.user_id == user_id,
                 Allocation.name == allocation_name, 
                 Allocation.category_id == await self._get_category_by_name(category_name, user_id))
            ).returning(Allocation.alloc_id)
        res = await self.db_session.execute(query)
        deleted_allocation_row = res.fetchone()
        if deleted_allocation_row:
            await self.db_session.commit()  
            return deleted_allocation_row[0]
        else:
            await self.db_session.rollback()  # Rollback in case of failure
            return None 

class PredictionDAL:
     def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    

class ReferenceDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def delete_referencebooks(self, ref_id: UUID, user_id: UUID) -> Union[UUID, None]:
        query = delete(ReferenceBook).where(
            and_(ReferenceBook.user_id == user_id,
                 ReferenceBook.ref_id == ref_id)
            ).returning(ReferenceBook.ref_id)
        res = await self.db_session.execute(query)
        deleted_row = res.fetchone()
        if deleted_row:
            await self.db_session.commit()  
            return deleted_row[0]
        else:
            await self.db_session.rollback()  # Rollback in case of failure
            return None 
    
    async def _create_referencebook(self, allocation_id : UUID, user_id: UUID, files : dict) -> ReferenceBook:
        if await self.is_reference_exist(allocation_id=allocation_id, user_id=user_id,):
            raise HTTPException(status_code=400, detail="The referencebooks already created for this allocation")
        new_refbook = ReferenceBook(
            user_id=user_id,
            alloc_id=allocation_id,
            contracts=files.get("contacts"),
            codes=files.get("codes"),
            fixedassets=files.get("fixedassets"),
            building_squares=files.get("building_squares"),
            contracts_to_building=files.get("contracts_to_building"),
        )
        self.db_session.add(new_refbook)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_refbook
    
    async def is_reference_exist(self, allocation_id: UUID, user_id: UUID) -> bool:
        query = select(ReferenceBook).where(
            and_(ReferenceBook.alloc_id == allocation_id,
            ReferenceBook.user_id == user_id
        ))
        res = await self.db_session.execute(query)
        if res.scalars().first():
            logger.warning(f"Reference found for allocation_id: {allocation_id} and user_id: {user_id}")
            return True
        else:
            logger.info(f"No reference found for allocation_id: {allocation_id} and user_id: {user_id}")
            return False
        
class BillDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def delete_bill(self, bill_id: UUID, user_id: UUID) -> Union[UUID, None]:
        query = delete(BillToPay).where(
            and_(BillToPay.user_id == user_id,
                 BillToPay.bill_id == bill_id)
            ).returning(BillToPay.bill_id)
        res = await self.db_session.execute(query)
        deleted_row = res.fetchone()
        if deleted_row:
            await self.db_session.commit()  
            return deleted_row[0]
        else:
            await self.db_session.rollback()  # Rollback in case of failure
            return None 
    
    async def _create_bill(self, allocation_id : UUID, user_id: UUID, files : dict) -> ReferenceBook:
        if await self.is_bill_exist(allocation_id=allocation_id, user_id=user_id,):
            raise HTTPException(status_code=400, detail="The bill already created for this allocation")
        new_bill = BillToPay(
            user_id=user_id,
            alloc_id=allocation_id,
            bills_to_pay=files.get("bills_to_pay")
        )
        self.db_session.add(new_bill)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_bill
    
    async def is_bill_exist(self, allocation_id: UUID, user_id: UUID) -> bool:
        query = select(BillToPay).where(
            and_(BillToPay.alloc_id == allocation_id,
            BillToPay.user_id == user_id
        ))
        res = await self.db_session.execute(query)
        if res.scalars().first():
            logger.warning(f"Reference found for allocation_id: {allocation_id} and user_id: {user_id}")
            return True
        else:
            logger.info(f"No reference found for allocation_id: {allocation_id} and user_id: {user_id}")
            return False