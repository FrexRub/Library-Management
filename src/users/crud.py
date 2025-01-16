import logging
from typing import Optional, TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import configure_logging
from src.core.exceptions import (
    ExceptDB,
    NotFindUser,
    EmailInUse,
    ExceptUser,
    ErrorInData,
)
from src.core.jwt_utils import create_hash_password
from src.users.models import User


if TYPE_CHECKING:
    from src.users.schemas import UserCreateSchemas

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def get_user_from_db(session: AsyncSession, username: str) -> User:
    logger.info("Start find user by username: %s" % username)
    stmt = select(User).where(User.username == username)
    res: Result = await session.execute(stmt)
    user: Optional[User] = res.scalars().one_or_none()
    if not user:
        logger.info("User by name %s not find" % username)
        raise NotFindUser(f"Not find user by username {username}")
    logger.info("User has benn found")
    return user


async def get_user_by_id(session: AsyncSession, id_user: int) -> User:
    logger.info("Start find user by id %d" % id_user)
    stmt = select(User).where(User.id == id_user)
    res: Result = await session.execute(stmt)
    user: User = res.scalars().first()
    logger.info("User by id %d has been found" % id_user)
    return user


async def find_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).filter(User.email == email)
    result: Result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_data: "UserCreateSchemas") -> int:
    result: Optional[User] = await find_user_by_email(
        session=session, email=user_data.email
    )
    if result:
        raise EmailInUse("The email address is already in use")

    try:
        result: User = await get_user_from_db(
            session=session, username=user_data.username
        )
    except NotFindUser:
        pass
    else:
        raise ExceptUser(
            "The user with the username: %s is already registered" % user_data.username
        )

    try:
        new_user: User = User(**user_data.model_dump())
    except ValueError as exc:
        raise ErrorInData(exc)
    else:
        new_user.hashed_password = create_hash_password(
            new_user.hashed_password
        ).decode()
        session.add(new_user)
        await session.commit()
        return new_user.id
