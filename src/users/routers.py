from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from src.core.config import COOKIE_NAME
from src.core.database import get_async_session
from src.core.exceptions import ErrorInData, NotFindUser, EmailInUse, ExceptUser
from src.core.jwt_utils import create_jwt, set_cookie, validate_password
from src.users.crud import get_user_from_db, create_user
from src.users.depends import current_superuser_user
from src.users.models import User
from src.users.schemas import UserCreateSchemas, LoginSchemas

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


@router.post("/login", response_class=Response, status_code=200)
async def userlogin(data_login: LoginSchemas, session=Depends(get_async_session)):
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


@router.get("/list", status_code=200)
async def get_list_users(session=Depends(get_async_session)):
    pass


# @router.get("/", response_model=list[Product])
# async def ger_products(
#     session: AsyncSession = Depends(db_helper.scope_session_dependency),
# ):
#     return await crud.get_products(session=session)
