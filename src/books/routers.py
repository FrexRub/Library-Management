from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status, Response
from fastapi_pagination import Page, paginate
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.exceptions import (
    ErrorInData,
    ExceptDB,
)
from src.books.crud import (
    create_book,
    get_books,
    update_book_db,
    delete_book_db,
    find_books_title,
    find_books_author,
)
from src.books.dependencies import book_by_id
from src.users.depends import (
    current_superuser_user,
    current_user_authorization,
)
from src.books.models import Book
from src.books.schemas import (
    BookUpdateSchemas,
    BookUpdatePartialSchemas,
    BookCreateSchemas,
    OutBookSchemas,
    OutBookFoolSchemas,
    BookFindSchemas,
    OutAuthorBooksSchemas,
)

if TYPE_CHECKING:
    from src.users.models import User

router = APIRouter(prefix="/books", tags=["Books"])


@router.post("/new", response_model=OutBookSchemas, status_code=status.HTTP_201_CREATED)
async def new_book(
    book: BookCreateSchemas,
    session: AsyncSession = Depends(get_async_session),
    user: "User" = Depends(current_superuser_user),
):
    try:
        result: Book = await create_book(session=session, book_in=book)
    except ExceptDB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error in data bases",
        )
    except ErrorInData as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    else:
        return result


@router.get(
    "/list",
    response_model=Page[OutBookFoolSchemas],
    status_code=status.HTTP_200_OK,
)
async def get_list_books(
    session: AsyncSession = Depends(get_async_session),
    user: "User" = Depends(current_user_authorization),
):
    return paginate(await get_books(session=session))


@router.get("/{book_id}/", response_model=OutBookSchemas)
async def get_book(
    user: "User" = Depends(current_user_authorization),
    book: Book = Depends(book_by_id),
):
    return book


@router.put("/{book_id}/", response_model=OutBookSchemas)
async def update_book(
    book_update: BookUpdateSchemas,
    user: "User" = Depends(current_superuser_user),
    book: Book = Depends(book_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        res = await update_book_db(session=session, book=book, book_update=book_update)
    except ErrorInData as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    else:
        return res


@router.patch("/{book_id}/", response_model=OutBookSchemas)
async def update_book(
    book_update: BookUpdatePartialSchemas,
    user: "User" = Depends(current_superuser_user),
    book: Book = Depends(book_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        res = await update_book_db(
            session=session, book=book, book_update=book_update, partial=True
        )
    except ErrorInData as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    else:
        return res


@router.delete("/{book_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    user: "User" = Depends(current_superuser_user),
    book: Book = Depends(book_by_id),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    try:
        await delete_book_db(session=session, book=book)
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )


@router.post("/title", response_model=Page[OutBookFoolSchemas])
async def find_book_by_title(
    text: BookFindSchemas,
    user: "User" = Depends(current_user_authorization),
    session: AsyncSession = Depends(get_async_session),
):
    return paginate(await find_books_title(session=session, text=text))


@router.post("/author", response_model=Page[OutAuthorBooksSchemas])
async def find_book_by_author(
    text: BookFindSchemas,
    user: "User" = Depends(current_user_authorization),
    session: AsyncSession = Depends(get_async_session),
):

    return paginate(await find_books_author(session=session, text=text))
