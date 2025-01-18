from typing import Annotated, TYPE_CHECKING
from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.authors.crud import get_author

if TYPE_CHECKING:
    from src.authors.models import Author


async def author_by_id(
    author_id: Annotated[int, Path],
    session: AsyncSession = Depends(get_async_session),
) -> "Author":
    author = await get_author(session=session, author_id=author_id)
    if author:
        return author
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Author {author_id} not found!",
    )
