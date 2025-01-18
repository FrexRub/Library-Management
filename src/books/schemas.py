from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_async_validation import async_field_validator

from src.core.database import async_session_maker
from src.genres.schemas import OutGenreSchemas
from src.authors.models import Author


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
    # @async_field_validator("id_author")
    # async def validator_id_author(self, value):
    #     async with async_session_maker() as session:
    #         author: Author = await session.get(Author, value)
    #
    #     if author is None:
    #         raise ValueError(f"Author {value} not found!")
    #     return value


class OutBookSchemas(BookBaseSchemas):
    id: int
    # genres_ids: list[OutGenreSchemas]

    model_config = ConfigDict(from_attributes=True)
