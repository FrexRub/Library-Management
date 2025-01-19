from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.exceptions import (
    ErrorInData,
    ExceptDB,
)
from src.library.crud import (
    create_receiving,
    return_receiving,
)
from src.books.dependencies import book_by_id
from src.users.depends import (
    current_superuser_user,
    current_user_authorization,
)
from src.books.models import Book
from src.users.models import User
from src.library.models import ReceivingBook
from src.library.schemas import (
    ReceivingCreateSchemas,
    OutReceivingSchemas,
    ReceivingReturnSchemas,
)


router = APIRouter(prefix="/library", tags=["library"])


@router.post(
    "/receiving",
    response_model=OutReceivingSchemas,
    status_code=status.HTTP_201_CREATED,
)
async def receiving_book(
    receiving: ReceivingCreateSchemas,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user_authorization),
):
    try:
        result: ReceivingBook = await create_receiving(
            session=session, receiving_in=receiving, user_in=user
        )
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    except ErrorInData as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    else:
        return result


@router.post(
    "/return",
    response_class=Response,
    status_code=status.HTTP_201_CREATED,
)
async def return_book(
    book_in: ReceivingReturnSchemas,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user_authorization),
):
    try:
        result: str = await return_receiving(
            session=session, book_in=book_in, user_in=user
        )
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    except ErrorInData as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    else:
        return result


#
# @router.get(
#     "/list", response_model=list[OutBookFoolSchemas], status_code=status.HTTP_200_OK
# )
# async def get_list_books(
#     session: AsyncSession = Depends(get_async_session),
#     user: "User" = Depends(current_user_authorization),
# ):
#     return await get_books(session=session)
#
#
# @router.get("/{book_id}/", response_model=OutBookSchemas)
# async def get_book(
#     user: "User" = Depends(current_user_authorization),
#     book: Book = Depends(book_by_id),
# ):
#     return book
#
#
# @router.put("/{book_id}/", response_model=OutBookSchemas)
# async def update_book(
#     book_update: BookUpdateSchemas,
#     user: "User" = Depends(current_superuser_user),
#     book: Book = Depends(book_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     try:
#         res = await update_book_db(session=session, book=book, book_update=book_update)
#     except ErrorInData as exp:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"{exp}",
#         )
#     else:
#         return res
#
#
# @router.patch("/{book_id}/", response_model=OutBookSchemas)
# async def update_book(
#     book_update: BookUpdatePartialSchemas,
#     user: "User" = Depends(current_superuser_user),
#     book: Book = Depends(book_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     try:
#         res = await update_book_db(
#             session=session, book=book, book_update=book_update, partial=True
#         )
#     except ErrorInData as exp:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"{exp}",
#         )
#     else:
#         return res
#
#
# @router.delete("/{book_id}/", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_book(
#     user: "User" = Depends(current_superuser_user),
#     book: Book = Depends(book_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ) -> None:
#     try:
#         await delete_book_db(session=session, book=book)
#     except ExceptDB as exp:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"{exp}",
#         )
