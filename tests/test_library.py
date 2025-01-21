from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from src.books.models import Book
from src.users.crud import get_user_from_db
from src.core.jwt_utils import create_jwt
from src.core.config import COOKIE_NAME

username_admin = "Testlibrary"
email_admin = "test_library@mail.ru"
password_admin = "1qaz!QAZ"

list_title_book = ["Test1", "Test2", "Test3", "Test4", "Test5", "Test6"]


async def test_user_for_library(client: AsyncClient):
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


@pytest.mark.parametrize("title_book", list_title_book)
async def test_new_book(title_book, client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "title": title_book,
        "description": "",
        "release_date": "1836-01-01",
        "count": 1,
        "id_author": 1,
        "genres_ids": [1],
    }
    response = await client.post("/books/new", cookies=cookies, json=data)

    assert response.status_code == 201
    assert "Test" in response.json()["title"]


async def test_receiving_book_not_authorized(client: AsyncClient):
    data = {
        "book_id": 1,
    }
    response = await client.post("/library/receiving", json=data)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


async def test_receiving_book_not_find(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "book_id": 10,
    }
    response = await client.post("/library/receiving", cookies=cookies, json=data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Not find book"


@pytest.mark.parametrize("id_book", list(range(1, 6)))
async def test_receiving_5books(id_book, client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "book_id": id_book,
    }
    response = await client.post("/library/receiving", cookies=cookies, json=data)
    book = await db_session.get(Book, id_book)

    assert response.status_code == 201
    assert book.count == 0


async def test_receiving_book_more_5(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "book_id": 1,
    }
    response = await client.post("/library/receiving", cookies=cookies, json=data)

    assert response.status_code == 400
    assert response.json()["detail"] == "The user has 5 books"


async def test_return_book(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "book_id": 1,
    }
    response = await client.post("/library/return", cookies=cookies, json=data)
    book = await db_session.get(Book, 1)

    assert response.status_code == 201
    assert book.count == 1


async def test_return_book_not_have(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    data = {
        "book_id": 1,
    }
    response = await client.post("/library/return", cookies=cookies, json=data)
    book = await db_session.get(Book, 1)

    assert response.status_code == 400
    assert response.json()["detail"] == "The user does not have this book"


async def test_list_book_on_hands(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/library/on-hands", cookies=cookies)

    assert response.status_code == 200
    assert len(response.json()) == 4


async def test_list_book_user_by_id(client: AsyncClient, db_session: AsyncSession):
    user = await get_user_from_db(db_session, username_admin)
    jwt: str = create_jwt(str(user.id))
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/library/1/", cookies=cookies)

    assert response.status_code == 200
    assert len(response.json()) == 4


async def test_list_book_user_by_id_not_permission(client: AsyncClient):
    response = await client.get("/library/1/")

    assert response.status_code == 403
