import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.genres.models import Genre
from src.genres.schemas import (
    GenreCreateSchemas,
    GenreUpdateSchemas,
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


async def update_genre_db(
    session: AsyncSession,
    genre: Genre,
    genre_update: GenreUpdateSchemas,
) -> Genre:
    logger.info("Start update genre")
    try:
        for (
            name,
            value,
        ) in genre_update.model_dump().items():  # Преобразовываем объект в словарь
            setattr(genre, name, value)
        await session.commit()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        await session.rollback()
        raise ExceptDB(exc)
    return genre


async def delete_genre_db(session: AsyncSession, genre: Genre) -> None:
    logger.info("Delete genre by id %d" % genre.id)
    await session.delete(genre)
    await session.commit()
