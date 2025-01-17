from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from src.core.config import COOKIE_NAME
from src.core.database import get_async_session
from src.core.exceptions import ErrorInData, NotFindUser, EmailInUse, ExceptUser
from src.core.jwt_utils import create_jwt, validate_password
from src.users.crud import get_user_from_db, create_user, get_users
from src.users.depends import current_superuser_user, current_user_authorization
from src.users.models import User
from src.users.schemas import UserCreateSchemas, LoginSchemas, OutUserSchemas

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/create", response_class=Response, status_code=status.HTTP_201_CREATED)
async def user_registration(
    user: UserCreateSchemas,
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    try:
        result: int = await create_user(session=session, user_data=user)
    except EmailInUse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email address is already in use",
        )
    except ExceptUser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user with the username: {user.username} is already registered",
        )
    except ErrorInData:
        pass
    else:
        return Response(status_code=status.HTTP_201_CREATED, content="Ok")


@router.post("/login", response_class=Response, status_code=status.HTTP_200_OK)
async def userlogin(
    data_login: LoginSchemas, session: AsyncSession = Depends(get_async_session)
):
    try:
        user: User = await get_user_from_db(
            session=session, username=data_login.username
        )
    except NotFindUser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user with the username: {data_login.username} not found",
        )

    if validate_password(
        password=data_login.password, hashed_password=user.hashed_password.encode()
    ):
        access_token: str = create_jwt(str(user.id))

        resp = Response(
            content="The user is logged in",
            status_code=status.HTTP_202_ACCEPTED,
        )
        resp.set_cookie(key=COOKIE_NAME, value=access_token, httponly=True)
        return resp
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error password for login: {data_login.username}",
        )


@router.get(
    "/list", response_model=list[OutUserSchemas], status_code=status.HTTP_200_OK
)
async def get_list_users(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser_user),
):
    return await get_users(session=session)
