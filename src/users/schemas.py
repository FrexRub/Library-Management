from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserIdSchemas(BaseModel):
    id: int


class UserCreateSchemas(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str = Field(alias="password")


class OutUserSchemas(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    registered_at: datetime


class LoginSchemas(BaseModel):
    username: str
    password: str
