from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.core.jwt_utils import create_jwt
from src.core.config import COOKIE_NAME

username_admin = "SRub"
email_admin = "frexxx@mail.ru"
password_admin = "1qaz!QAZ"

username = "Bob"
email = "Bob@mail.ru"
password = "1qaz!QAZ"


async def test_get_client(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200


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
    assert response.json()["id"] == 1


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


async def test_set_user_admin(db_session: AsyncSession):
    user = await db_session.get(User, 1)
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


async def test_create_new_post(client: AsyncClient):
    jwt: str = create_jwt("1")
    cookies = {COOKIE_NAME: jwt}
    response = await client.get("/users/list", cookies=cookies)

    assert response.status_code == 200


# async def test_get_main(client: AsyncClient):
#     response = await client.get("/posts")
#     assert response.status_code == 307
#
#
# async def test_create_user(db_session: AsyncSession):
#     hash_password = create_hash_password(PASSWORD).decode()
#     user: User = User(
#         username=USERNAME,
#         email=EMAIL,
#         hashed_password=hash_password,
#         is_active=True,
#         is_superuser=False,
#     )
#     assert user.username == USERNAME
#     num: int = await add_user_to_db(db_session, user)
#     assert num == 1
#
#
# async def test_create_user_raises(db_session: AsyncSession):
#     hash_password = create_hash_password(PASSWORD).decode()
#     user: User = User(
#         username=USERNAME,
#         email=EMAIL,
#         hashed_password=hash_password,
#         is_active=True,
#         is_superuser=False,
#     )
#
#     with pytest.raises(ExceptDB):
#         await add_user_to_db(db_session, user)
#
#
# def test_create_jwt():
#     jwt: str = create_jwt("1")
#     assert jwt.count(".") == 2
#
#
# async def test_create_new_post(client: AsyncClient):
#     # В случае успеха в эндпоинте идет переадресация на страницу index.html
#     jwt: str = create_jwt("1")
#     cookies = {COOKIE_NAME: jwt}
#     post = {"title": "Test", "content": "Test post"}
#     response = await client.post("/posts", data=post, cookies=cookies)
#     assert response.status_code == 307
#
#
# async def test_endpoint_test(client: AsyncClient):
#     post = {"title": "Test", "content": "Test post"}  # Данные для полей формы
#     jwt: str = create_jwt("1")
#     cookies = {COOKIE_NAME: jwt}  # Генерация куков для авторизации
#     response = await client.post("/posts/test", data=post, cookies=cookies)
#     assert response.status_code == 200
#     assert response.json()["title"] == "Test"
#
#
# async def test_add_new_post_bd(db_session: AsyncSession):
#     post: PostCreate = PostCreate(title="Test", body="Test post")
#     await add_new_post(session=db_session, post=post, id_user=1)
#     post_db: Post = await db_session.get(Post, 1)
#     assert post_db.id == 1
