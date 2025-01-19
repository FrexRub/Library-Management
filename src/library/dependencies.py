from typing import Annotated, TYPE_CHECKING
from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.books.crud import get_book

if TYPE_CHECKING:
    from src.books.models import Book


async def book_by_id(
    book_id: Annotated[int, Path],
    session: AsyncSession = Depends(get_async_session),
) -> "Book":
    book = await get_book(session=session, book_id=book_id)
    if book:
        return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book {book_id} not found!",
    )
