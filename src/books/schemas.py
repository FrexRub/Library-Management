from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BookBaseSchemas(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=250)
    release_date: date
    count: int = Field(ge=0)
    id_author: int = Field(ge=0)
    genres_ids: list[int]


class BookUpdateSchemas(BookBaseSchemas):
    pass


class BookUpdatePartialSchemas(BookUpdateSchemas):
    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[date] = None
    count: Optional[int] = None
    id_author: Optional[int] = None
    genres_ids: Optional[list[int]] = None


class BookCreateSchemas(BookBaseSchemas):
    pass


class AuthorSchemas(BaseModel):
    id: int
    full_name: str


class GenreSchemas(BaseModel):
    title: str


class OutBookSchemas(BookBaseSchemas):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OutBookFoolSchemas(BaseModel):
    id: int
    title: str
    description: str
    author: AuthorSchemas
    release_date: date
    count: int
    genres: list[str]
