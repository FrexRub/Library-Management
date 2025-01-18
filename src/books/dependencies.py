from typing import Annotated, TYPE_CHECKING
from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.genres.crud import get_genre

if TYPE_CHECKING:
    from src.genres.models import Genre


async def genre_by_id(
    genre_id: Annotated[int, Path],
    session: AsyncSession = Depends(get_async_session),
) -> "Genre":
    genre = await get_genre(session=session, genre_id=genre_id)
    if genre:
        return genre
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Genre {genre_id} not found!",
    )
