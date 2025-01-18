from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.exceptions import (
    ErrorInData,
    ExceptDB,
)
from src.genres.crud import (
    create_genre,
    get_genres,
    update_genre_db,
)
from src.genres.dependencies import genre_by_id
from src.users.depends import (
    current_superuser_user,
)
from src.genres.models import Genre
from src.genres.schemas import (
    GenreCreateSchemas,
    OutGenreSchemas,
    GenreUpdateSchemas,
)

if TYPE_CHECKING:
    from src.users.models import User

router = APIRouter(prefix="/genres", tags=["genres"])


@router.post(
    "/new", response_model=OutGenreSchemas, status_code=status.HTTP_201_CREATED
)
async def new_author(
    genre: GenreCreateSchemas,
    session: AsyncSession = Depends(get_async_session),
    user: "User" = Depends(current_superuser_user),
):
    try:
        result: Genre = await create_genre(session=session, genre_in=genre)
    except ExceptDB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error in data bases",
        )
    except ErrorInData:
        pass
    else:
        return result


@router.get(
    "/list", response_model=list[OutGenreSchemas], status_code=status.HTTP_200_OK
)
async def get_list_genre(
    session: AsyncSession = Depends(get_async_session),
    user: "User" = Depends(current_superuser_user),
):
    return await get_genres(session=session)


@router.get("/{genre_id}/", response_model=OutGenreSchemas)
async def get_genre(
    user: "User" = Depends(current_superuser_user),
    genre: Genre = Depends(genre_by_id),
):
    return genre


@router.put("/{genre_id}/", response_model=OutGenreSchemas)
async def update_genre(
    genre_update: GenreUpdateSchemas,
    user: "User" = Depends(current_superuser_user),
    genre: Genre = Depends(genre_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        res = await update_genre_db(
            session=session, genre=genre, genre_update=genre_update
        )
    except ExceptDB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in data base",
        )
    else:
        return res


#
# @router.delete("/{author_id}/", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user: "User" = Depends(current_superuser_user),
#     author: Author = Depends(author_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ) -> None:
#     await delete_author_db(session=session, author=author)
