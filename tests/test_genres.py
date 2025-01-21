from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.genres.models import Genre
from src.users.crud import get_user_from_db
from src.core.jwt_utils import create_jwt
from src.core.config import COOKIE_NAME

username_admin = "TestGenre"
email_admin = "test_genre@mail.ru"
password_admin = "1qaz!QAZ"


async def test_user_for_genre(client: AsyncClient):
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


async def test_new_genre(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "title": "Роман",
    }
    response = await client.post("/genres/new", cookies=cookies, json=data)

    assert response.status_code == 201
    assert response.json()["title"] == "Роман"


async def test_get_list_genres(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/genres/list", cookies=cookies)

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Роман"


async def test_get_list_genre_not_admin(client: AsyncClient):
    response = await client.get("/genres/list")

    assert response.status_code == 403


async def test_get_genre_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/genres/1/", cookies=cookies)

    assert response.status_code == 200
    assert response.json()["title"] == "Роман"


async def test_put_genre_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "title": "Test1",
    }
    response = await client.put("/genres/1/", cookies=cookies, json=data)

    assert response.status_code == 200
    assert response.json()["title"] == "Test1"


async def test_delete_genre_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.delete("/genres/1/", cookies=cookies)

    user = await db_session.get(Genre, 1)
    assert response.status_code == 204
    assert user is None
