import logging
from typing import Optional, TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors.crud import get_author
from src.books.models import Book
from src.books.schemas import (
    BookUpdateSchemas,
    BookUpdatePartialSchemas,
    BookCreateSchemas,
)
from src.core.exceptions import ErrorInData, ExceptDB
from src.core.config import configure_logging
from src.authors.models import Author
from src.genres.models import Genre

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def create_book(session: AsyncSession, book_in: BookCreateSchemas) -> Book:
    logger.info("Start create new book")
    author: Author = await get_author(
        session=session, author_id=book_in.model_dump()["id_author"]
    )
    if author is None:
        raise ErrorInData("Nor find author")

    genres_id: list[int] = book_in.model_dump()["genres_ids"]
    for genre_id in genres_id:
        if await session.get(Genre, genre_id) is None:
            raise ErrorInData(f"Not find genres with id {genre_id}")

    try:
        book: Book = Book(**book_in.model_dump())
    except ValueError as exc:
        logger.exception("Error in value %s", exc)
        raise ErrorInData(exc)
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        raise ExceptDB(exc)
    else:
        session.add(book)
        await session.commit()
        return book


#
# async def get_genres(session: AsyncSession) -> list[Genre]:
#     logger.info("Getting a list of genres")
#     try:
#         stmt = select(Genre).order_by(Genre.id)
#         result: Result = await session.execute(stmt)
#         genres = result.scalars().all()
#     except SQLAlchemyError as exc:
#         logger.exception("Error in data base %s", exc)
#     else:
#         return list(genres)
#
#
# async def get_genre(session: AsyncSession, genre_id: int) -> Optional[Genre]:
#     logger.info("Getting genre by id %d" % genre_id)
#     return await session.get(Genre, genre_id)
#
#
# async def update_genre_db(
#     session: AsyncSession,
#     genre: Genre,
#     genre_update: GenreUpdateSchemas,
# ) -> Genre:
#     logger.info("Start update genre")
#     try:
#         for (
#             name,
#             value,
#         ) in genre_update.model_dump().items():  # Преобразовываем объект в словарь
#             setattr(genre, name, value)
#         await session.commit()
#     except SQLAlchemyError as exc:
#         logger.exception("Error in data base %s", exc)
#         await session.rollback()
#         raise ExceptDB(exc)
#     return genre
#
#
# async def delete_genre_db(session: AsyncSession, genre: Genre) -> None:
#     logger.info("Delete genre by id %d" % genre.id)
#     await session.delete(genre)
#     await session.commit()
