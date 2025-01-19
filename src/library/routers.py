from typing import Optional

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
    get_books,
)
from src.users.depends import (
    current_superuser_user,
    current_user_authorization,
)
from src.books.schemas import OutBookFoolSchemas
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


@router.get("/on-hands", response_model=list[OutBookFoolSchemas])
async def get_books_user(
    user: "User" = Depends(current_user_authorization),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await get_books(session=session, user_id=user.id)
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    return result


@router.get("/{user_id}/", response_model=list[OutBookFoolSchemas])
async def get_book_user_by_id(
    user_id: int,
    user: "User" = Depends(current_superuser_user),
    session: AsyncSession = Depends(get_async_session),
):
    user: Optional[User] = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {user_id} not found",
        )
    try:
        result = await get_books(session=session, user_id=user_id)
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    return result
