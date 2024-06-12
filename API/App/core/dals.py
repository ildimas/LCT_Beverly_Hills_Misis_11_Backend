from typing import Union
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
# from core.db import async_session
from models import User

class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, name: str, email: str, password: str) -> User:
        new_user = User(name=name,email=email,password=password)
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = update(User).\
            where (and_(User.user_id == user_id, User.is_active == True)).\
            values(is_active=False).\
            returning(User.user_id)
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row:
            return deleted_user_id_row[0]     
        
    # async def update_user
  
# if __name__ == "__main__":
#     asy_session = async_session
#     ud = UserDAL(asy_session)
#     ud.create_user("stepan", "kalushko", "stepa@gmail.com", "saddssdaasd")