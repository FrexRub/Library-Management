from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.users.crud import get_user_from_db
from src.core.jwt_utils import create_jwt
from src.core.config import COOKIE_NAME

username_admin = "TestUser"
email_admin = "test_user@mail.ru"
password_admin = "1qaz!QAZ"

username = "Bob"
email = "Bob@mail.ru"
password = "1qaz!QAZ"


async def test_create_user(client: AsyncClient):
    user = {
        "username": username_admin,
        "first_name": "",
        "last_name": "",
        "email": email_admin,
        "password": password_admin,
    }  # Данные для полей формы
    response = await client.post("/users/create", json=user)
    assert response.status_code == 201
    assert response.json()["username"] == username_admin


async def test_create_user_bad_email(client: AsyncClient):
    user = {
        "username": username,
        "first_name": "",
        "last_name": "",
        "email": email_admin,
        "password": password,
    }  # Данные для полей формы
    response = await client.post("/users/create", json=user)
    assert response.status_code == 400
    assert response.json()["detail"] == "The email address is already in use"


async def test_create_user_bad_password(client: AsyncClient):
    user = {
        "username": username,
        "first_name": "",
        "last_name": "",
        "email": email,
        "password": "password",
    }  # Данные для полей формы
    response = await client.post("/users/create", json=user)
    assert response.status_code == 422


async def test_create_user_not_admin(client: AsyncClient):
    user = {
        "username": username,
        "first_name": "",
        "last_name": "",
        "email": email,
        "password": password,
    }  # Данные для полей формы
    response = await client.post("/users/create", json=user)
    assert response.status_code == 201
    assert response.json()["username"] == username


async def test_set_user_admin(db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    user.is_superuser = True
    await db_session.commit()
    assert user.is_superuser


async def test_login_user(client: AsyncClient):
    user = {
        "username": username_admin,
        "password": password_admin,
    }  # Данные для полей формы
    response = await client.post("/users/login", json=user)
    print(response.content)
    assert response.status_code == 202
    assert response.cookies.get(COOKIE_NAME) != None


async def test_get_list_user_admin(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/users/list", cookies=cookies)

    assert response.status_code == 200


async def test_get_list_user_not_admin(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/users/list", cookies=cookies)

    assert response.status_code == 403


async def test_get_user_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/users/2/", cookies=cookies)

    assert response.status_code == 200
    assert response.json()["id"] == 2


async def test_put_user_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "first_name": "Test1",
        "last_name": "test1",
        "email": "test@mail.com",
    }
    response = await client.put("/users/2/", cookies=cookies, json=data)

    assert response.status_code == 200
    assert response.json()["first_name"] == "Test1"


async def test_patch_user_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {"first_name": "Test2"}
    response = await client.patch("/users/2/", cookies=cookies, json=data)

    assert response.status_code == 200
    assert response.json()["first_name"] == "Test2"


async def test_delete_user_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.delete("/users/2/", cookies=cookies)

    user = await db_session.get(User, 2)
    assert response.status_code == 204
    assert user is None
