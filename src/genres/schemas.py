from typing import Optional
from datetime import date

from pydantic import BaseModel, ConfigDict


class GenreBaseSchemas(BaseModel):
    title: str


class GenreUpdateSchemas(GenreBaseSchemas):
    pass


class GenreCreateSchemas(GenreBaseSchemas):
    pass


class OutGenreSchemas(GenreBaseSchemas):
    id: int

    model_config = ConfigDict(from_attributes=True)
