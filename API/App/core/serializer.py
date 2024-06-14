import re
import uuid
from typing import Optional, Union

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic import constr
from pydantic import EmailStr
from pydantic import field_validator
from API.App.core.models import User

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    model_config = {
        'from_attributes': True
    }
        

class ShowUser(TunedModel):
    user_id: uuid.UUID
    email: EmailStr
    
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise HTTPException(
                status_code=422, detail="password should be at least length 8"
            )
        return value

class DeleteUserResponse(BaseModel):
    deleted_user_id: Union[uuid.UUID, None]

class Token(BaseModel):
    access_token: str
    token_type: str
    
class CreateCategorySerializer(BaseModel):  
    name: str  
    
class DeleteCategorySerializer(BaseModel):
    category_id: Union[uuid.UUID, None]
    
class CreateAllocationSerializer(BaseModel):
    name: str
    category_name: str
        
class ShowAllocationSerializer(TunedModel):
    name: str
    category_id: uuid.UUID
    user_id: uuid.UUID
    
class DeleteAllocationSerializer(BaseModel):
    allocation_id : Union[uuid.UUID, None]
    
class ShowAllCategoriesSerializer(TunedModel):
    category_id: uuid.UUID
    name: str
    user_id: uuid.UUID
    
class ShowAllAllocationSerializer(TunedModel):
    name: str
    user_id: uuid.UUID
    category_id: uuid.UUID
    allocation_id: uuid.UUID
    
    
#!####### Bills ##########

#!########################

#?####### Predictions ##########

#?##############################