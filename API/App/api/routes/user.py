from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from API.App.core.models import User
from API.App.core.db import engine, async_session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Any
from API.App.core.dals import UserDAL
from sqlalchemy.ext.asyncio import AsyncSession
from API.App.core.hashing import Hasher
from API.App.core.serializer import UserCreate, ShowUser, DeleteUserResponse
from dotenv import load_dotenv
from API.App.core.db import get_db
load_dotenv()


user_router = APIRouter()

@user_router.post("/createuser", response_model=ShowUser)
async def create_new_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)

@user_router.post("/deleteuser", response_model=DeleteUserResponse)
async def delete_user(body: DeleteUserResponse, db: AsyncSession = Depends(get_db)) -> DeleteUserResponse:
    return await _deativate_user(body, db)



#Externa; functional for endpoint
async def _create_new_user(body: UserCreate, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(name=body.name, email=body.email, password=Hasher.get_password_hash(body.password))
        return ShowUser(user_id=user.user_id, name=user.name, email=user.email, is_active=user.is_active)

async def _deativate_user(body: DeleteUserResponse, session) -> DeleteUserResponse:
    async with session.begin():
        user_dal = UserDAL(session)
        del_id = await user_dal.delete_user(user_id=body.deleted_user_id)
        return DeleteUserResponse(deleted_user_id=del_id)