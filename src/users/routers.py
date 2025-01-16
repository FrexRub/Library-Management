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
from src.users.schemas import UserCreateSchemas

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/create", response_class=Response, status_code=status.HTTP_201_CREATED)
async def user_registration(
    request: Request,
    user: UserCreateSchemas,
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    try:
        result: int = await create_user(session=session, user_data=user)
    except EmailInUse as exc:
        return Response(content=exc, status_code=400)
    except ExceptUser as exc:
        return Response(content=exc, status_code=400)
    except ValueError as exc:
        return Response(content=f"Error in the data {exc}", status_code=400)
    else:
        return Response(status_code=status.HTTP_201_CREATED, content="Ok")
