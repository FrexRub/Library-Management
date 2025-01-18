import logging
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors.models import Author
from src.authors.schemas import AuthorCreateSchemas, OutAuthorSchemas
from src.core.exceptions import ErrorInData, ExceptDB
from src.core.config import configure_logging

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def create_author(
    session: AsyncSession, author_in: AuthorCreateSchemas
) -> Author:
    logger.info("Start create new author")
    try:
        author: Author = Author(**author_in.model_dump())
    except ValueError as exc:
        logger.exception("Error in value %s", exc)
        raise ErrorInData(exc)
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        raise ExceptDB(exc)
    else:
        session.add(author)
        await session.commit()
        return author


async def get_authors(session: AsyncSession) -> list[Author]:
    logger.info("Getting a list of authors")
    try:
        stmt = select(Author).order_by(Author.id)
        result: Result = await session.execute(stmt)
        authors = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
    else:
        return list(authors)


async def get_author(session: AsyncSession, author_id: int) -> Optional[Author]:
    logger.info("Getting author by id %d" % author_id)
    return await session.get(Author, author_id)
