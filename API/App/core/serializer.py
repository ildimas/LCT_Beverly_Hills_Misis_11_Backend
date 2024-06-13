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
    model_config = ConfigDict(from_attributes=True)
        

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
    
class ShowCategorySerializer(BaseModel):
    name: str
    user_id: uuid.UUID
    
class CreateAllocationSerializer(BaseModel):
    name: str
    category_name: str
        
class ShowAllocationSerializer(BaseModel):
    name: str
    category_name: str
    user_id: uuid.UUID
