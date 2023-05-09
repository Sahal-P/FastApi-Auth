from pydantic import BaseModel, Field, validator, EmailStr
from bson import ObjectId
import pydantic, datetime
from bson import ObjectId
from typing import Optional
# pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str


class PyObjectId(ObjectId):
    """ Custom Type for reading MongoDB IDs """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid object_id")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# 
class Users(BaseModel):
    _id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str = Field(...)
    last_name: Optional[str] = ""
    phone_number:str = Field(...)
    username: str = Field(...)
    email: str = Field(...)
    password:str = Field(...)
    is_admin: str = Field(...)
    is_superuser: str = Field(...)
    is_blocked: str = Field(...)
    

    class Config:
        allow_population_by_field_name =True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: lambda v:str}
        schema_extra = {
            "example": {
                "first_name": "Can",
                "last_name": "Can",
                "phone_number": "Ilgu",
                "username": "Ilgu",
                "is_blocked": "Ilgu",
                "is_admin": "Ilgu",
                "is_superuser": "Ilgu",
                "email": "can@gmail.com",
                "password": "123456"
            }
        }

      
class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "can@gmail.com",
                "password": "123456"
            }
        }
        
class UserToken(BaseModel):
    user_id: str = Field(...)
    token: str = Field(...)
    created_at: datetime.datetime = None

