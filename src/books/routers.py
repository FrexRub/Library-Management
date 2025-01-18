from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.exceptions import (
    ErrorInData,
    ExceptDB,
)
from src.books.crud import (
    create_book,
)
from src.books.dependencies import genre_by_id
from src.users.depends import (
    current_superuser_user,
)
from src.books.models import Book
from src.books.schemas import (
    BookUpdateSchemas,
    BookUpdatePartialSchemas,
    BookCreateSchemas,
    OutBookSchemas,
)

if TYPE_CHECKING:
    from src.users.models import User

router = APIRouter(prefix="/books", tags=["books"])


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


# @router.get(
#     "/list", response_model=list[OutGenreSchemas], status_code=status.HTTP_200_OK
# )
# async def get_list_genre(
#     session: AsyncSession = Depends(get_async_session),
#     user: "User" = Depends(current_superuser_user),
# ):
#     return await get_genres(session=session)
#
#
# @router.get("/{genre_id}/", response_model=OutGenreSchemas)
# async def get_genre(
#     user: "User" = Depends(current_superuser_user),
#     genre: Genre = Depends(genre_by_id),
# ):
#     return genre
#
#
# @router.put("/{genre_id}/", response_model=OutGenreSchemas)
# async def update_genre(
#     genre_update: GenreUpdateSchemas,
#     user: "User" = Depends(current_superuser_user),
#     genre: Genre = Depends(genre_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     try:
#         res = await update_genre_db(
#             session=session, genre=genre, genre_update=genre_update
#         )
#     except ExceptDB:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Error in data base",
#         )
#     else:
#         return res
#
#
# @router.delete("/{genre_id}/", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_genre(
#     user: "User" = Depends(current_superuser_user),
#     genre: Genre = Depends(genre_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ) -> None:
#     await delete_genre_db(session=session, genre=genre)
