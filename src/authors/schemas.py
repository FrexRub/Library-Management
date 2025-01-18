from typing import Optional
from datetime import date

from pydantic import BaseModel, ConfigDict


class AuthorBaseSchemas(BaseModel):
    full_name: str
    biography: str
    date_birth: date


class AuthorCreateSchemas(AuthorBaseSchemas):
    pass


class OutAuthorSchemas(AuthorBaseSchemas):
    id: int

    model_config = ConfigDict(from_attributes=True)
