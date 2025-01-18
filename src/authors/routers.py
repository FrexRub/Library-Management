from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.exceptions import (
    ErrorInData,
    ExceptDB,
)
from src.authors.crud import (
    create_author,
    get_authors,
    update_author_db,
    delete_author_db,
)
from src.authors.dependencies import author_by_id
from src.users.depends import (
    current_superuser_user,
)
from src.authors.models import Author
from src.authors.schemas import (
    AuthorCreateSchemas,
    OutAuthorSchemas,
    AuthorUpdateSchemas,
    AuthorUpdatePartialSchemas,
)

if TYPE_CHECKING:
    from src.users.models import User

router = APIRouter(prefix="/authors", tags=["authors"])


@router.post(
    "/new", response_model=OutAuthorSchemas, status_code=status.HTTP_201_CREATED
)
async def new_author(
    author: AuthorCreateSchemas,
    session: AsyncSession = Depends(get_async_session),
    user: "User" = Depends(current_superuser_user),
):
    try:
        result: Author = await create_author(session=session, author_in=author)
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


@router.get(
    "/list", response_model=list[OutAuthorSchemas], status_code=status.HTTP_200_OK
)
async def get_list_author(
    session: AsyncSession = Depends(get_async_session),
    user: "User" = Depends(current_superuser_user),
):
    return await get_authors(session=session)


@router.get("/{author_id}/", response_model=OutAuthorSchemas)
async def get_author(
    user: "User" = Depends(current_superuser_user),
    author: Author = Depends(author_by_id),
):
    return author


@router.put("/{author_id}/", response_model=OutAuthorSchemas)
async def update_author(
    author_update: AuthorUpdateSchemas,
    user: "User" = Depends(current_superuser_user),
    author: Author = Depends(author_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        res = await update_author_db(
            session=session, author=author, author_update=author_update
        )
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    else:
        return res


@router.patch("/{author_id}/", response_model=OutAuthorSchemas)
async def update_author_partial(
    author_update: AuthorUpdatePartialSchemas,
    user: "User" = Depends(current_superuser_user),
    author: Author = Depends(author_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        res = await update_author_db(
            session=session, author=author, author_update=author_update, partial=True
        )
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    else:
        return res


@router.delete("/{author_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    user: "User" = Depends(current_superuser_user),
    author: Author = Depends(author_by_id),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    try:
        await delete_author_db(session=session, author=author)
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
