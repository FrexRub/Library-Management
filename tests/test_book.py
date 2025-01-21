from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.books.models import Book
from src.users.crud import get_user_from_db
from src.core.jwt_utils import create_jwt
from src.core.config import COOKIE_NAME

username_admin = "TestBook"
email_admin = "test_book@mail.ru"
password_admin = "1qaz!QAZ"


async def test_user_for_book(client: AsyncClient):
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


async def test_new_book(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "title": "Капитанская дочка",
        "description": "действие происходит во время восстания Емельяна Пугачёва",
        "release_date": "1836-01-01",
        "count": 1,
        "id_author": 1,
        "genres_ids": [1],
    }
    response = await client.post("/books/new", cookies=cookies, json=data)

    assert response.status_code == 201
    assert response.json()["title"] == "Капитанская дочка"


async def test_get_list_books(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/books/list", cookies=cookies)

    assert response.status_code == 200
    assert response.json()["items"][0]["title"] == "Капитанская дочка"


async def test_get_list_books_not_admin(client: AsyncClient):
    response = await client.get("/books/list")

    assert response.status_code == 403


async def test_get_book_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/books/1/", cookies=cookies)

    assert response.status_code == 200
    assert response.json()["title"] == "Капитанская дочка"


async def test_put_book_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "title": "Test1",
        "description": "действие происходит во время восстания Емельяна Пугачёва",
        "release_date": "1836-01-01",
        "count": 1,
        "id_author": 1,
        "genres_ids": [1],
    }
    response = await client.put("/books/1/", cookies=cookies, json=data)

    assert response.status_code == 200
    assert response.json()["title"] == "Test1"


async def test_find_book_by_title(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {"text": "Test"}
    response = await client.post("/books/title", cookies=cookies, json=data)

    assert response.status_code == 200
    assert response.json()["items"][0]["title"] == "Test1"


async def test_find_book_by_author(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {"text": "Александр"}
    response = await client.post("/books/author", cookies=cookies, json=data)

    assert response.status_code == 200
    assert response.json()["items"][0]["author"]["full_name"] == "Александр Пушкин"
    assert response.json()["items"][0]["books"][0]["title"] == "Test1"


async def test_delete_book_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.delete("/books/1/", cookies=cookies)

    user = await db_session.get(Book, 1)
    assert response.status_code == 204
    assert user is None
