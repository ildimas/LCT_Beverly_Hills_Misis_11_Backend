from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from API.App.core.models import User
from API.App.core.db import engine, async_session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Union
from API.App.core.dals import UserDAL
from sqlalchemy.ext.asyncio import AsyncSession
from API.App.core.hashing import Hasher
from API.App.core.serializer import UserCreate, ShowUser, DeleteUserResponse
from dotenv import load_dotenv
from API.App.core.db import get_db
from sqlalchemy.exc import IntegrityError
from API.App.api.routes.auth import get_current_user_from_token
load_dotenv()


user_router = APIRouter()

@user_router.get("/", response_model=ShowUser)
async def get_user(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> ShowUser:
    return await _get_user(email=current_user.email, uuid=current_user.user_id, session=db)

@user_router.post("/", response_model=ShowUser)
async def create_new_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db)

@user_router.delete("/", response_model=DeleteUserResponse)
async def deactivate_user(body: DeleteUserResponse, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> DeleteUserResponse:
    user_for_deactivation = await _get_user_by_id(body.deleted_user_id, db)
    if user_for_deactivation is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {body.deleted_user_id} not found."
        )
    elif body.deleted_user_id == current_user.user_id:
        return await _deativate_user(body, db)
    else:
        raise HTTPException(status_code=405, detail="You are not allowed to delete other users")

###########################################################################
############################UTILITY########################################
###########################################################################

async def _get_user(email, uuid, session) -> ShowUser:
    async with session.begin():
        return ShowUser(user_id=uuid, email=email)


async def _create_new_user(body: UserCreate, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        try:
            user = await user_dal.create_user(email=body.email, password=Hasher.get_password_hash(body.password))
        except IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e.orig):
                raise HTTPException(status_code=400, detail="Email already exists")
            else:
                raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return ShowUser(user_id=user.user_id, email=user.email)

async def _deativate_user(body: DeleteUserResponse, session) -> DeleteUserResponse:
    async with session.begin():
        user_dal = UserDAL(session)
        del_id = await user_dal.delete_user(user_id=body.deleted_user_id)
        return DeleteUserResponse(deleted_user_id=del_id)
    
async def _get_user_by_id(user_id, session) -> Union[User, None]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(
            user_id=user_id,
        )
        if user is not None:
            return user
