from typing import Optional
from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

PATTERN_PASSWORD = (
    r'^(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[0-9])(?=.*?[!"#\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_'
    r"`\{\|}~])[a-zA-Z0-9!\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_`\{\|}~]{8,}$"
)


class UserBaseSchemas(BaseModel):
    username: str = Field(min_length=2)
    first_name: str
    last_name: str
    email: EmailStr


class UserUpdateSchemas(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserUpdatePartialSchemas(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreateSchemas(UserBaseSchemas):
    hashed_password: str = Field(alias="password")

    @field_validator("username")
    def username_alphanumeric(cls, value):
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username must be alphanumeric")
        return value

    @field_validator("hashed_password")
    def validate_password(cls, value):
        if not re.match(PATTERN_PASSWORD, value):
            raise ValueError("Invalid password")
        return value


class OutUserSchemas(UserBaseSchemas):
    registered_at: datetime
    id: int

    model_config = ConfigDict(from_attributes=True)


class LoginSchemas(BaseModel):
    username: str
    password: str
