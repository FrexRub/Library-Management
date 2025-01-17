from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
import uvicorn

from src.users.routers import router as router_users

app = FastAPI()

app.include_router(router_users)


@app.get("/", response_class=HTMLResponse)
def index(response: Response):
    return HTMLResponse("Library Management")


if __name__ == "__main__":
    uvicorn.run("main:app")
