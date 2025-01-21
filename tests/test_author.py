from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.authors.models import Author
from src.users.crud import get_user_from_db
from src.core.jwt_utils import create_jwt
from src.core.config import COOKIE_NAME

username_admin = "TestAuthor"
email_admin = "test_author@mail.ru"
password_admin = "1qaz!QAZ"


async def test_user_for_author(client: AsyncClient):
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


async def test_set_user_admin(db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    user.is_superuser = True
    await db_session.commit()
    assert user.is_superuser


async def test_new_author(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "full_name": "Александр Пушкин",
        "biography": "",
        "date_birth": "1837-02-10",
    }
    response = await client.post("/authors/new", cookies=cookies, json=data)

    assert response.status_code == 201
    assert response.json()["full_name"] == "Александр Пушкин"


async def test_get_list_author(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/authors/list", cookies=cookies)

    assert response.status_code == 200
    assert response.json()[0]["full_name"] == "Александр Пушкин"


async def test_get_list_author_not_admin(client: AsyncClient):
    response = await client.get("/authors/list")

    assert response.status_code == 403


async def test_get_author_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/authors/1/", cookies=cookies)

    assert response.status_code == 200
    assert response.json()["full_name"] == "Александр Пушкин"


async def test_put_author_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "full_name": "Test1",
        "biography": "",
        "date_birth": "1837-02-10",
    }
    response = await client.put("/authors/1/", cookies=cookies, json=data)

    assert response.status_code == 200
    assert response.json()["full_name"] == "Test1"


async def test_patch_author_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {"full_name": "Test2"}
    response = await client.patch("/authors/1/", cookies=cookies, json=data)

    assert response.status_code == 200
    assert response.json()["full_name"] == "Test2"


async def test_delete_author_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.delete("/authors/1/", cookies=cookies)

    user = await db_session.get(Author, 1)
    assert response.status_code == 204
    assert user is None
