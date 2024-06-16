from fastapi import  HTTPException, status, APIRouter, Depends
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from API.App.core.models import User
from typing import List
from API.App.core.dals import CategoryDAL
from API.App.core.serializer import CreateCategorySerializer, ShowAllCategoriesSerializer, DeleteCategorySerializer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from API.App.api.routes.auth import get_current_user_from_token
from API.App.core.db import get_db
load_dotenv()

category_router = APIRouter()

@category_router.get("/", response_model=List[ShowAllCategoriesSerializer])
async def show_all_cateories(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> List[ShowAllCategoriesSerializer]:
    return await _show_all_categories(db, current_user)

@category_router.post("/", response_model=ShowAllCategoriesSerializer)
async def create_new_cateory(body: CreateCategorySerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> ShowAllCategoriesSerializer:
    return await _create_new_category(body, db, current_user)

@category_router.delete("/", response_model=DeleteCategorySerializer)
async def delete_category(body: CreateCategorySerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> DeleteCategorySerializer:
    return await _delete_category(body, db, current_user)


###########################################################################
############################UTILITY########################################
###########################################################################

async def _create_new_category(body: CreateCategorySerializer, session, current_user : User ) -> ShowAllCategoriesSerializer:
    async with session.begin():
        cat_dal = CategoryDAL(session)
        cat = await cat_dal.create_category(name=body.name, user_id=current_user.user_id)
        return ShowAllCategoriesSerializer(name=cat.name, user_id=cat.user_id, category_id=cat.category_id)
    
async def _delete_category(body: CreateCategorySerializer, session, current_user : User ) -> DeleteCategorySerializer:
    async with session.begin():
        cat_dal = CategoryDAL(session)
        result = await cat_dal.delete_category(body.name, current_user.user_id)
        return DeleteCategorySerializer(category_id=result)
    
async def _show_all_categories(session, current_user : User ) -> ShowAllCategoriesSerializer:
    async with session.begin():
        cat_dal = CategoryDAL(session)
        result_categories = await cat_dal.show_all_categories(current_user.user_id)
        return [ShowAllCategoriesSerializer.model_validate(category) for category in result_categories]
    