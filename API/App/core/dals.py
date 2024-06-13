from typing import Union
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
# from core.db import async_session
from models import User, Category, Allocation

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

    async def create_category(self, name: str, user_id: UUID) -> Category:
        new_category = Category(name=name, user_id=user_id)
        self.db_session.add(new_category)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_category
    
    async def delete_category(self, category_name: str, user_id: UUID) -> str:
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
        
    async def create_allocation(self, name : str, category_name : str, user_id: UUID) -> Allocation:
        new_allocation = Allocation(name=name, category_id = self._get_categoty_by_name(category_name), user_uuid=user_id)
        self.db_session.add(new_allocation)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_allocation
    
    
    async def _get_categoty_by_name(self, name: str) -> Union[UUID, None]:
        query = select(Category).where(Category.name == name)
        res = await self.db_session.execute(query)
        category_row = res.fetchone()
        if category_row is not None:
            return category_row[0].category_id
        return None
        