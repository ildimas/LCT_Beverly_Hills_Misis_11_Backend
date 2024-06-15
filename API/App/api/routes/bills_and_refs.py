from fastapi import  HTTPException, status, APIRouter, Depends, Query, File, UploadFile, Form
import sys
from uuid import UUID
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from API.App.core.models import User, Category
from typing import List, Optional
from API.App.core.dals import ReferenceDAL, BillDAL
from API.App.core.serializer import ReferenceBooksSerializer, DeleteReferenceBooksSerializer, BillsSerializer, DeleteBillsSerializer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from API.App.api.routes.auth import get_current_user_from_token
from API.App.core.db import get_db
load_dotenv()



billsandrefs_router = APIRouter()

@billsandrefs_router.post("/",  response_model=BillsSerializer)
async def create_new_bill(alloc_id: UUID = Form(...),
                             bills_to_pay: UploadFile = File(None),
                             db: AsyncSession = Depends(get_db), 
                             current_user: User = Depends(get_current_user_from_token)) -> BillsSerializer:
    return await _create_new_bill(alloc_id, db, current_user, bills_to_pay=bills_to_pay)
    
@billsandrefs_router.delete("/", response_model=DeleteBillsSerializer)
async def delete_refbook(body : DeleteBillsSerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> DeleteBillsSerializer:
    return await _delete_bill(body, db, current_user)


@billsandrefs_router.post("/refs",  response_model=ReferenceBooksSerializer)
async def create_new_refbook(alloc_id: UUID = Form(...),
                             contacts: UploadFile = File(None),
                             codes: UploadFile = File(None),
                             fixedassets: UploadFile = File(None),
                             building_squares: UploadFile = File(None),
                             contracts_to_building: UploadFile = File(None),
                             db: AsyncSession = Depends(get_db), 
                             current_user: User = Depends(get_current_user_from_token)) -> ReferenceBooksSerializer:
    return await _create_new_referencebook(alloc_id, db, current_user, contacts=contacts, codes=codes, fixedassets=fixedassets,
                                           building_squares=building_squares, contracts_to_building=contracts_to_building)
    
@billsandrefs_router.delete("/refs", response_model=DeleteReferenceBooksSerializer)
async def delete_refbook(body : DeleteReferenceBooksSerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)) -> DeleteReferenceBooksSerializer:
    return await _delete_refbook(body, db, current_user)

###########################################################################
############################UTILITY########################################
###########################################################################

async def _create_new_referencebook(allocation_id, session, current_user : User, 
                                    contacts, codes, fixedassets, building_squares, contracts_to_building) -> ReferenceBooksSerializer:
    async with session.begin():
        ref_dal = ReferenceDAL(session)
        files = {
            "contacts": await contacts.read() if contacts else None,
            "codes": await codes.read() if codes else None,
            "fixedassets": await fixedassets.read() if fixedassets else None,
            "building_squares": await building_squares.read() if building_squares else None,
            "contracts_to_building": await contracts_to_building.read() if contracts_to_building else None,
        }
        ref = await ref_dal._create_referencebook(allocation_id=allocation_id,
                                                  user_id=current_user.user_id,
                                                  files=files)
        return ReferenceBooksSerializer(alloc_id=ref.alloc_id, ref_id=ref.ref_id)
    
async def _delete_refbook(body: DeleteReferenceBooksSerializer, session, current_user : User ) -> DeleteReferenceBooksSerializer:
    async with session.begin():
        dal = ReferenceDAL(session)
        result = await dal.delete_referencebooks(ref_id=body.ref_id, user_id=current_user.user_id)
        return DeleteReferenceBooksSerializer(ref_id=result)
    
async def _create_new_bill(allocation_id, session, current_user : User, bills_to_pay) -> BillsSerializer:
    async with session.begin():
        bill_dal = BillDAL(session)
        files = {
            "bills_to_pay": await bills_to_pay.read() if bills_to_pay else None
        }
        bill = await bill_dal._create_bill(allocation_id=allocation_id, user_id=current_user.user_id, files=files)
        return BillsSerializer(alloc_id=bill.alloc_id, bill_id=bill.bill_id)
    
async def _delete_bill(body: DeleteBillsSerializer, session, current_user : User ) -> DeleteBillsSerializer:
    async with session.begin():
        dal = ReferenceDAL(session)
        result = await dal.delete_referencebooks(bill_id=body.bill_id, user_id=current_user.user_id)
        return DeleteBillsSerializer(bill_id=result)