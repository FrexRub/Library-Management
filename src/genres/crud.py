import logging
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.genres.models import Genre
from src.genres.schemas import (
    GenreCreateSchemas,
    OutGenreSchemas,
    GenreUpdateSchemas,
    GenreUpdatePartialSchemas,
)
from src.core.exceptions import ErrorInData, ExceptDB
from src.core.config import configure_logging

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def create_genre(session: AsyncSession, genre_in: GenreCreateSchemas) -> Genre:
    logger.info("Start create new genre")
    try:
        genre: Genre = Genre(**genre_in.model_dump())
    except ValueError as exc:
        logger.exception("Error in value %s", exc)
        raise ErrorInData(exc)
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        raise ExceptDB(exc)
    else:
        session.add(genre)
        await session.commit()
        return genre


async def get_genres(session: AsyncSession) -> list[Genre]:
    logger.info("Getting a list of genres")
    try:
        stmt = select(Genre).order_by(Genre.id)
        result: Result = await session.execute(stmt)
        genres = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
    else:
        return list(genres)


async def get_genre(session: AsyncSession, genre_id: int) -> Optional[Genre]:
    logger.info("Getting genre by id %d" % genre_id)
    return await session.get(Genre, genre_id)


#
# async def update_author_db(
#     session: AsyncSession,
#     author: Author,
#     author_update: Union[AuthorUpdateSchemas, AuthorUpdatePartialSchemas],
#     partial: bool = False,
# ) -> Author:
#     logger.info("Start update author")
#     try:
#         for name, value in author_update.model_dump(
#             exclude_unset=partial
#         ).items():  # Преобразовываем объект в словарь
#             setattr(author, name, value)
#         await session.commit()
#     except SQLAlchemyError as exc:
#         logger.exception("Error in data base %s", exc)
#         await session.rollback()
#         raise ExceptDB(exc)
#     return author
#
#
# async def delete_author_db(session: AsyncSession, author: Author) -> None:
#     logger.info("Delete author by id %d" % author.id)
#     await session.delete(author)
#     await session.commit()
