from fastapi import  HTTPException, status, APIRouter, Depends, Query
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from API.App.core.models import User, Category
from typing import List, Optional
from API.App.core.dals import PredictionDAL
from API.App.core.serializer import PredictionsInitSerializer, BasePredictionInput, BasePredictionResponseSerializer, SearchAtributesPredictionsSerializer, InitSearchAtributesPredictionsSerializer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from dotenv import load_dotenv
from API.App.api.routes.auth import get_current_user_from_token
from API.App.core.db import get_db
load_dotenv()


prediction_router = APIRouter()

@prediction_router.post("/search", response_model=List[SearchAtributesPredictionsSerializer])
async def predict_price(body: InitSearchAtributesPredictionsSerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return await _search_for_content(content=body.content, search_atribute=body.search_atribute, allocation_id=body.alloc_id, session=db, current_user=current_user.user_id)


@prediction_router.post("/predict")
async def predict_price(body: PredictionsInitSerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return await _predict_price_utils(allocation_id=body.allocation_id, session=db, current_user=current_user.user_id)

@prediction_router.post("/check")
async def predict_price(body: PredictionsInitSerializer, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return await _prediction_health_check(allocation_id=body.allocation_id, session=db, current_user=current_user.user_id)


@prediction_router.post("/main_ledger_id", response_model=List[BasePredictionResponseSerializer])
async def search_by_main_ledger(body: BasePredictionInput, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return await _search_funnel(allocation_id=body.alloc_id, session=db, current_user=current_user.user_id,
                                searchable_atribute="main_ledger_id", searchable_value=body.searchable_value, months=body.months_to_show)
    
@prediction_router.post("/fixed_assets_class", response_model=List[BasePredictionResponseSerializer])
async def search_by_fixed_assets_class(body: BasePredictionInput, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return await _search_funnel(allocation_id=body.alloc_id, session=db, current_user=current_user.user_id,
                            searchable_atribute="fixed_assets_class", searchable_value=body.searchable_value, months=body.months_to_show)
    
@prediction_router.post("/fixed_assets_id", response_model=List[BasePredictionResponseSerializer])
async def search_by_fixed_assets_id(body: BasePredictionInput, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return await _search_funnel(allocation_id=body.alloc_id, session=db, current_user=current_user.user_id,
                            searchable_atribute="fixed_assets_id", searchable_value=body.searchable_value, months=body.months_to_show)    

@prediction_router.post("/building", response_model=List[BasePredictionResponseSerializer])
async def search_by_building(body: BasePredictionInput, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user_from_token)):
    return await _search_funnel(allocation_id=body.alloc_id, session=db, current_user=current_user.user_id,
                                searchable_atribute="building", searchable_value=body.searchable_value, months=body.months_to_show)

###########################################################################
############################UTILITY########################################
###########################################################################

async def _predict_price_utils(allocation_id : UUID, session, current_user: UUID):
    async with session.begin():
        dal = PredictionDAL(session)
        if await dal.health_check(allocation_id, current_user):
            return {"message": "Predictions are already calculated for this allocation !"}
        else:
            await dal.start_prediction(allocation_id=allocation_id, user_id=current_user)
            return {"message": "Prediction is sucsessfull !"}
        
async def _search_funnel(allocation_id : UUID, session, current_user: UUID, searchable_value : str, searchable_atribute : str , months : int):
    async with session.begin():
        dal = PredictionDAL(session)
        predictions = await dal.search_for_predictions(allocation_id=allocation_id, user_id=current_user, searchable_atribute=searchable_atribute, searchable_value=searchable_value, months=months)
        return [BasePredictionResponseSerializer(building=prediction.building, searchable_atribute=searchable_atribute, time_period=prediction.time_period, price=prediction.price) for prediction in predictions]

async def _search_for_content(content : str, search_atribute: str, allocation_id : UUID, session, current_user : UUID):
    async with session.begin():
        dal = PredictionDAL(session)
        results = await dal.full_text_search(content=content, search_atribute=search_atribute, allocation_id=allocation_id, user_id=current_user)
        return [SearchAtributesPredictionsSerializer(content=content) for content in results]
    
async def _prediction_health_check(allocation_id : UUID, session, current_user : UUID):
    async with session.begin():
        dal = PredictionDAL(session)
        status = await dal.health_check(allocation_id, current_user)
        return {"content" : f"{status}"}
    