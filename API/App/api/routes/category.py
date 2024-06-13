from fastapi import  HTTPException, status, APIRouter, Depends
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from API.App.core.models import User
from API.App.core.dals import CategoryDAL
from API.App.core.serializer import CreateCategorySerializer, ShowCategorySerializer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from API.App.api.routes.auth import get_current_user_from_token
from API.App.core.db import get_db
load_dotenv()

category_router = APIRouter()

@category_router.post("/", response_model=ShowCategorySerializer)
async def create_new_cateory(body: CreateCategorySerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> ShowCategorySerializer:
    return await _create_new_category(body, db, current_user)

@category_router.delete("/", response_model=ShowCategorySerializer)
async def delete_category(body: CreateCategorySerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> ShowCategorySerializer:
    return await _delete_category(body, db, current_user)

# @category_router.get("/", response_model=ShowCategorySerializer)

###########################################################################
############################UTILITY########################################
###########################################################################

async def _create_new_category(body: CreateCategorySerializer, session, current_user : User ) -> ShowCategorySerializer:
    async with session.begin():
        cat_dal = CategoryDAL(session)
        try:
            cat = await cat_dal.create_category(name=body.name, user_id=current_user.user_id)
        except IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e.orig):
                raise HTTPException(status_code=400, detail="This category already exists")
            else:
                raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return ShowCategorySerializer(name=cat.name, user_id=cat.user_id)
    
async def _delete_category(body: CreateCategorySerializer, session, current_user : User ) -> ShowCategorySerializer:
    async with session.begin():
        cat_dal = CategoryDAL(session)
        cat = await cat_dal.delete_category(body.name, current_user.user_id)
        return ShowCategorySerializer(name=body.name, user_id=current_user.user_id)
    
