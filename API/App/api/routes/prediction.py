from fastapi import  HTTPException, status, APIRouter, Depends, Query
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from API.App.core.models import User, Category
from typing import List, Optional
from API.App.core.dals import AllocationDAL
from API.App.core.serializer import * #!
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from API.App.api.routes.auth import get_current_user_from_token
from API.App.core.db import get_db
load_dotenv()


prediction_router = APIRouter()

@prediction_router.get("/")
def hello_smal_redeployment_system():
    return {"message": "hello this endpoint showed here automaticly"}
###########################################################################
############################UTILITY########################################
###########################################################################