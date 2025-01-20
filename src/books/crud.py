import logging
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors.crud import get_author
from src.books.models import Book
from src.books.schemas import (
    BookUpdateSchemas,
    BookUpdatePartialSchemas,
    BookCreateSchemas,
    OutBookFoolSchemas,
    AuthorSchemas,
    BookFindSchemas,
    OutBookShortSchemas,
    OutAuthorBooksSchemas,
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
        logger.info("Not find author")
        raise ErrorInData("Not find author")

    genres_id: list[int] = book_in.model_dump()["genres_ids"]
    for genre_id in genres_id:
        if await session.get(Genre, genre_id) is None:
            logger.info("Not find genres with id %s" % genre_id)
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
        logger.info("New book create")
        return book


async def book_to_schema(session: AsyncSession, book: Book) -> OutBookFoolSchemas:
    # OutBookFoolSchemas
    author: AuthorSchemas = AuthorSchemas(
        id=book.author.id, full_name=book.author.full_name
    )
    list_genres = list()
    for i_genres in book.genres_ids:
        genres = await session.get(Genre, i_genres)
        list_genres.append(genres.title if genres else "отсутствует")
    res: OutBookFoolSchemas = OutBookFoolSchemas(
        id=book.id,
        title=book.title,
        description=book.description,
        author=author,
        release_date=book.release_date,
        count=book.count,
        genres=list_genres,
    )
    return res


async def get_books(session: AsyncSession) -> list[OutBookFoolSchemas]:
    logger.info("Getting a list of books")
    try:
        stmt = select(Book).options(joinedload(Book.author)).order_by(Book.id)
        result: Result = await session.execute(stmt)
        books = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
    else:
        list_books = list()
        for book in books:  # type: Book
            list_books.append(await book_to_schema(session=session, book=book))

        return list_books


async def get_book(session: AsyncSession, book_id: int) -> Optional[Book]:
    logger.info("Getting genre by id %d" % book_id)
    return await session.get(Book, book_id)


async def update_book_db(
    session: AsyncSession,
    book: Book,
    book_update: Union[BookUpdateSchemas, BookUpdatePartialSchemas],
    partial: bool = False,
) -> Book:
    logger.info("Start update book")
    try:
        for name, value in book_update.model_dump(exclude_unset=partial).items():
            if name == "id_author" and await session.get(Author, value) is None:
                logger.info("Not find author with id %s" % value)
                raise ErrorInData(f"Not find author with id {value}")
            elif name == "genres_ids":
                for genre_id in value:
                    if await session.get(Genre, genre_id) is None:
                        logger.info("Not find genres with id %s" % genre_id)
                        raise ErrorInData(f"Not find genres with id {genre_id}")
                else:
                    setattr(book, name, value)
            else:
                setattr(book, name, value)
        await session.commit()

    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        await session.rollback()
        raise ExceptDB(exc)
    return book


async def delete_book_db(session: AsyncSession, book: Book) -> None:
    logger.info("Delete book by id %d" % book.id)
    try:
        await session.delete(book)
        await session.commit()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
        await session.rollback()
        raise ExceptDB(exc)


async def find_books_title(
    session: AsyncSession, text: BookFindSchemas
) -> list[OutBookFoolSchemas]:
    find_text: str = text.model_dump()["text"]
    logger.info("Start find books by title %s" % find_text)
    try:
        stmt = (
            select(Book)
            .filter(Book.title.ilike(f"%{find_text}%"))
            .options(joinedload(Book.author))
            .order_by(Book.id)
        )
        result: Result = await session.execute(stmt)
        books = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
    else:
        list_books = list()
        for book in books:  # type: Book
            list_books.append(await book_to_schema(session=session, book=book))

        return list_books


async def find_books_author(
    session: AsyncSession, text: BookFindSchemas
) -> list[OutAuthorBooksSchemas]:
    find_text: str = text.model_dump()["text"]
    logger.info("Start find books by author %s" % find_text)
    try:
        stmt = (
            select(Author)
            .filter(Author.full_name.ilike(f"%{find_text}%"))
            .options(selectinload(Author.books))
            .order_by(Author.id)
        )
        result: Result = await session.execute(stmt)
        authors = result.scalars().all()
    except SQLAlchemyError as exc:
        logger.exception("Error in data base %s", exc)
    else:
        list_author_books = list()
        for author in authors:
            out_author = AuthorSchemas(id=author.id, full_name=author.full_name)
            list_books = list()
            for book in author.books:  # type: Book
                out_book = OutBookShortSchemas(
                    title=book.title,
                    description=book.description,
                    release_date=book.release_date,
                    count=book.count,
                )
                list_books.append(out_book)

            list_author_books.append(
                OutAuthorBooksSchemas(author=out_author, books=list_books)
            )

        return list_author_books
