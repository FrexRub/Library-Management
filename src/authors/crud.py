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
