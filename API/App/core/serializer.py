import re
import uuid
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict, Field
from pydantic import constr
from pydantic import EmailStr
from pydantic import field_validator
from API.App.core.models import User
from fastapi import  HTTPException
from API.App.core.dals import ReferenceDAL

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")

class FileResponseModel(BaseModel):
    url: str
    
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
    alloc_id: uuid.UUID
    
    
#!####### Bills ##########




# class CreateReferenceBooksSerializer(BaseModel):
#     alloc_id: uuid.UUID
    
class ReferenceBooksSerializer(TunedModel):
    alloc_id: uuid.UUID
    ref_id: uuid.UUID
    
class DeleteReferenceBooksSerializer(TunedModel):
    ref_id: Union[uuid.UUID, None]
    

class BillsSerializer(TunedModel):
    alloc_id: uuid.UUID
    bill_id: uuid.UUID
    
class DeleteBillsSerializer(TunedModel):
    bill_id: Union[uuid.UUID, None]
    
    
#!########################

#?####### Predictions ##########

#?##############################

######## Allocation config ##########

# class AllocationConfig(BaseModel):
    


#####################################
