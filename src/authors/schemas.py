from typing import Optional
from datetime import date

from pydantic import BaseModel, ConfigDict


class AuthorBaseSchemas(BaseModel):
    full_name: str
    biography: str
    date_birth: date


class AuthorUpdateSchemas(AuthorBaseSchemas):
    pass


class AuthorUpdatePartialSchemas(AuthorBaseSchemas):
    full_name: Optional[str] = None
    biography: Optional[str] = None
    date_birth: Optional[date] = None


class AuthorCreateSchemas(AuthorBaseSchemas):
    pass


class OutAuthorSchemas(AuthorBaseSchemas):
    id: int

    model_config = ConfigDict(from_attributes=True)
