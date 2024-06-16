from fastapi import  HTTPException, status, APIRouter, Depends, Query
import sys
from uuid import UUID
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from API.App.core.models import User, Category
from typing import List, Optional
from API.App.core.dals import AllocationDAL
from API.App.core.serializer import CreateAllocationSerializer, ShowAllocationSerializer, DeleteAllocationSerializer, ShowAllAllocationSerializer, ProcessAllocationInput, DownloadAllocation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from API.App.api.routes.auth import get_current_user_from_token
from API.App.core.db import get_db
import io
load_dotenv()

allocation_router = APIRouter()

@allocation_router.get("/", response_model=List[ShowAllAllocationSerializer])
async def show_all_acllocations(db: AsyncSession = Depends(get_db), 
                                current_user: User = Depends(get_current_user_from_token),
                                category_name: Optional[str] = Query(None, description="Limit the allocations by category")
                                ) -> List[ShowAllAllocationSerializer]:
    return await _show_all_allocations(db, current_user, category=category_name)

@allocation_router.post("/", response_model=ShowAllocationSerializer)
async def create_new_allocation(body: CreateAllocationSerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> ShowAllocationSerializer:
    return await _create_new_allocation(body, db, current_user)

@allocation_router.delete("/", response_model=DeleteAllocationSerializer)
async def delete_allocation(body: CreateAllocationSerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> DeleteAllocationSerializer:
    return await _delete_allocation(body, db, current_user)

@allocation_router.post("/process")
async def configure_allocation(body : ProcessAllocationInput, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return await _start_allocation_process(db, body.allocation_id, current_user, body.rules)

@allocation_router.post("/download")
async def download_allocation(body : DownloadAllocation, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return await _download_content(db, body.allocation_id, current_user, body.xlsx_or_csv)


###########################################################################
############################UTILITY########################################
###########################################################################


async def _create_new_allocation(body: CreateAllocationSerializer, session, current_user : User ) -> ShowAllocationSerializer:
    async with session.begin():
        all_dal = AllocationDAL(session)
        all = await all_dal.create_allocation(name=body.name, category_name=body.category_name, user_id=current_user.user_id)
        return ShowAllocationSerializer(name=all.name, category_id=all.category_id, user_id=all.user_id)


async def _delete_allocation(body: CreateAllocationSerializer, session, current_user : User ) -> DeleteAllocationSerializer:
    async with session.begin():
        all_dal = AllocationDAL(session)
        result = await all_dal.delete_allocation(body.name, body.category_name, current_user.user_id)
        return DeleteAllocationSerializer(allocation_id=result)
    
async def _show_all_allocations(session, current_user : User , category : Optional[str]) -> ShowAllAllocationSerializer:
    async with session.begin():
        dal = AllocationDAL(session)
        result_allocations = await dal.show_all_allocations(current_user.user_id, category=category)
        return [ShowAllAllocationSerializer.model_validate(allocation) for allocation in result_allocations]
    

async def _start_allocation_process(session, allocation_id : UUID ,current_user : User, rules : dict):
    #! process
    async with session.begin():
        dal = AllocationDAL(session)
        await dal.validate_and_process_allocation(allocation_id=allocation_id, user_id=current_user.user_id, rules=rules)
        return {"message": "Allocation have been sucsessfuly created and stored in database"}
    
    
async def _download_content(session, allocation_id : UUID, current_user : User, xlsx_or_csv: bool):
    async with session.begin():
        dal = AllocationDAL(session)
        file_content = await dal.download_allocation_content(allocation_id=allocation_id, user_id = current_user.user_id, xlsx_or_csv=xlsx_or_csv)
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment;filename=result.{'csv' if xlsx_or_csv else 'xlsx'}"}
        )   
        # return {"message" : f"File was sucssefully downloaded in {'csv' if xlsx_or_csv else 'xlsx'}"}