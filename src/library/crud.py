import logging
from typing import Optional, Union
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors.crud import get_author
from src.books.models import Book
from src.users.models import User
from src.library.models import ReceivingBook
from src.authors.models import Author
from src.genres.models import Genre
from src.library.schemas import (
    ReceivingCreateSchemas,
    ReceivingReturnSchemas,
)
from src.core.exceptions import ErrorInData, ExceptDB
from src.core.config import configure_logging
from src.books.crud import book_to_schema
from src.books.schemas import OutBookFoolSchemas
from src.users.crud import get_user_by_id


configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


async def create_receiving(
    session: AsyncSession, receiving_in: ReceivingCreateSchemas, user_in: User
) -> ReceivingBook:
    # ReceivingBook
    logger.info("Start create receiving book")
    book: Optional[Book] = await session.get(Book, receiving_in.model_dump()["book_id"])

    if book is None:
        logger.info("Not find book")
        raise ErrorInData("Not find book")

    stmt = select(ReceivingBook).filter(ReceivingBook.user_id == user_in.id)
    result: Result = await session.execute(stmt)
    books_user = result.scalars().all()
    if len(books_user) >= 5:
        logger.info("The user has 5 books")
        raise ErrorInData("The user has 5 books")

    if book.count == 0:
        logger.info("These books are not available")
        raise ErrorInData("These books are not available")

    stmt = (
        select(User)
        .filter(User.id == user_in.id)
        .options(selectinload(User.books).joinedload(ReceivingBook.book))
    )
    result: Result = await session.execute(stmt)
    current_user = result.scalars().first()

    date_of_return = datetime.now() + timedelta(days=14)
    receiving_book = ReceivingBook(
        date_of_return=date_of_return,
    )

    try:
        receiving_book.book = book
        current_user.books.append(receiving_book)
        book.count -= 1
        await session.commit()
    except IntegrityError as exc:
        logger.warning("The user already has this book")
        await session.rollback()
        raise ExceptDB("The user already has this book")

    return receiving_book


async def return_receiving(
    session: AsyncSession, book_in: ReceivingReturnSchemas, user_in: User
) -> str:
    logger.info("Start return book in library")
    book_id: int = book_in.model_dump()["book_id"]
    stmt = select(ReceivingBook).filter(
        and_(ReceivingBook.user_id == user_in.id, ReceivingBook.book_id == book_id)
    )
    result: Result = await session.execute(stmt)
    books_user = result.scalars().first()
    if books_user is None:
        logger.info("The user does not have this book")
        raise ErrorInData("The user does not have this book")

    book: Optional[Book] = await session.get(Book, book_id)
    if book is None:
        logger.info("Not find book")
        raise ErrorInData("Not find book")

    try:
        await session.delete(books_user)
        book.count += 1
        await session.commit()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        await session.rollback()
        raise ExceptDB(exc)
    return "The book has been returned to the library"


async def get_books(session: AsyncSession, user_id: int) -> list[OutBookFoolSchemas]:
    logger.info("Getting a list of books user %s" % user_id)
    try:
        stmt = select(ReceivingBook).filter(ReceivingBook.user_id == user_id)
        result: Result = await session.execute(stmt)
        list_books = result.scalars().all()

    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        raise ExceptDB("Error in data base")
    else:
        list_id_books = list()
        for book in list_books:
            list_id_books.append(book.book_id)

        stmt = (
            select(Book)
            .filter(Book.id.in_(list_id_books))
            .options(joinedload(Book.author))
            .order_by(Book.id)
        )
        result: Result = await session.execute(stmt)
        books = result.scalars().all()

        list_books = list()
        for book in books:  # type: Book
            list_books.append(await book_to_schema(session=session, book=book))

        return list_books


# async def get_book(session: AsyncSession, book_id: int) -> Optional[Book]:
#     logger.info("Getting genre by id %d" % book_id)
#     return await session.get(Book, book_id)
#
#
# async def update_book_db(
#     session: AsyncSession,
#     book: Book,
#     book_update: Union[BookUpdateSchemas, BookUpdatePartialSchemas],
#     partial: bool = False,
# ) -> Book:
#     logger.info("Start update book")
#     try:
#         for name, value in book_update.model_dump(exclude_unset=partial).items():
#             if name == "id_author" and await session.get(Author, value) is None:
#                 logger.info("Not find author with id %s" % value)
#                 raise ErrorInData(f"Not find author with id {value}")
#             elif name == "genres_ids":
#                 for genre_id in value:
#                     if await session.get(Genre, genre_id) is None:
#                         logger.info("Not find genres with id %s" % genre_id)
#                         raise ErrorInData(f"Not find genres with id {genre_id}")
#                 else:
#                     setattr(book, name, value)
#             else:
#                 setattr(book, name, value)
#         await session.commit()
#
#     except SQLAlchemyError as exc:
#         logger.exception("Error in data base %s", exc)
#         await session.rollback()
#         raise ExceptDB(exc)
#     return book
#
#
# async def delete_book_db(session: AsyncSession, book: Book) -> None:
#     logger.info("Delete book by id %d" % book.id)
#     try:
#         await session.delete(book)
#         await session.commit()
#     except SQLAlchemyError as exc:
#         logger.exception("Error in data base %s", exc)
#         await session.rollback()
#         raise ExceptDB(exc)
