from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.exceptions import (
    ErrorInData,
    ExceptDB,
)
from src.authors.crud import create_author, get_authors
from src.authors.dependencies import author_by_id
from src.users.depends import (
    current_superuser_user,
)
from src.authors.models import Author
from src.authors.schemas import AuthorCreateSchemas, OutAuthorSchemas

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


#
#
# @router.put("/{id_user}/", response_model=OutUserSchemas)
# async def update_user(
#     user_update: UserUpdateSchemas,
#     user: User = Depends(user_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     try:
#         res = await update_user_db(session=session, user=user, user_update=user_update)
#     except UniqueViolationError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Duplicate email",
#         )
#     else:
#         return res
#
#
# @router.patch("/{id_user}/", response_model=OutUserSchemas)
# async def update_user_partial(
#     user_update: UserUpdatePartialSchemas,
#     user: User = Depends(user_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     try:
#         res = await update_user_db(
#             session=session, user=user, user_update=user_update, partial=True
#         )
#     except UniqueViolationError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Duplicate email",
#         )
#     else:
#         return res
#
#
# @router.delete("/{id_user}/", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user: User = Depends(user_by_id),
#     super_user: User = Depends(current_superuser_user),
#     session: AsyncSession = Depends(get_async_session),
# ) -> None:
#     await delete_user_db(session=session, user=user)
