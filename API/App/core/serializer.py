import re
import uuid
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic import constr
from pydantic import EmailStr
from pydantic import field_validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
        

class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    email: EmailStr
    is_active: bool
    
    
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value
    
    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise HTTPException(
                status_code=422, detail="password should be at least length 8"
            )
        return value

class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]
    email: Optional[EmailStr]

    @field_validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @field_validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value
