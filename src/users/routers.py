from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from src.core.config import COOKIE_NAME
from src.core.database import get_async_session
from src.core.exceptions import ExceptDB, NotFindUser, EmailInUse, ExceptUser
from src.core.jwt_utils import create_jwt, set_cookie, validate_password
from src.users.crud import get_user_from_db, create_user
from src.users.depends import current_superuser_user
from src.users.models import User
from src.users.schemas import UserCreateSchemas, LoginSchemas

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/create", response_class=Response, status_code=status.HTTP_201_CREATED)
async def user_registration(
    request: Request,
    user: UserCreateSchemas,
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    try:
        result: int = await create_user(session=session, user_data=user)
    except EmailInUse:
        return Response(content="The email address is already in use", status_code=400)
    except ExceptUser:
        return Response(
            content="The user with the username: %s is already registered"
            % user.username,
            status_code=400,
        )
    else:
        return Response(status_code=status.HTTP_201_CREATED, content="Ok")


@router.post("/login", response_class=Response, status_code=200)
async def userlogin(
    request: Request, data_login: LoginSchemas, session=Depends(get_async_session)
):
    try:
        user: User = await get_user_from_db(
            session=session, username=data_login.username
        )
    except NotFindUser:
        return Response(content="User not found", status_code=400)
    if validate_password(
        password=data_login.password, hashed_password=user.hashed_password.encode()
    ):
        resp = Response(
            content="The user is logged in",
            status_code=200,
        )
        resp.set_cookie(key=COOKIE_NAME, value="token", httponly=True)
        return resp
    else:
        return Response(content="Error password", status_code=400)
