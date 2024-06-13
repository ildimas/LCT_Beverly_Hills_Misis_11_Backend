from fastapi import  HTTPException, status, APIRouter, Depends
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from API.App.core.models import User
from API.App.core.dals import AllocationDAL
from API.App.core.serializer import CreateAllocationSerializer, ShowAllocationSerializer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from API.App.api.routes.auth import get_current_user_from_token
from API.App.core.db import get_db
load_dotenv()

allocation_router = APIRouter()

@allocation_router.post("/", response_model=ShowAllocationSerializer)
async def create_new_cateory(body: CreateAllocationSerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> ShowAllocationSerializer:
    return await _create_new_allocation(body, db, current_user)

###########################################################################
############################UTILITY########################################
###########################################################################


async def _create_new_allocation(body: CreateAllocationSerializer, session, current_user : User ) -> ShowAllocationSerializer:
    async with session.begin():
        all_dal = AllocationDAL(session)
        try:
            all = await all_dal.create_allocation(name=body.name, category_name=body.category_name, user_id=current_user)
        except IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e.orig):
                raise HTTPException(status_code=400, detail="This category already exists")
            else:
                raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return ShowAllocationSerializer(name=all.name, user_id=all.user_id)


