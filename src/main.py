from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
import uvicorn

from src.users.routers import router as router_users
from src.authors.routers import router as router_authors
from src.genres.routers import router as router_genres
from src.books.routers import router as router_books
from src.library.routers import router as router_library

app = FastAPI()

app.include_router(router_users)
app.include_router(router_authors)
app.include_router(router_genres)
app.include_router(router_books)
app.include_router(router_library)


@app.get("/", response_class=HTMLResponse)
def index(response: Response):
    return HTMLResponse("Library Management")


if __name__ == "__main__":
    uvicorn.run("main:app")
