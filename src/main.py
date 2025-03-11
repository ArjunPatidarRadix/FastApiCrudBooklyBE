"""
Tutorial reference : https://www.youtube.com/watch?v=TO4aQ3ghFOc
Documentation : https://jod35.github.io/fastapi-beyond-crud-docs/site/chapter5/
Git code: https://github.com/jod35/fastapi-beyond-CRUD/blob/main/src/__init__.py
"""

from fastapi import FastAPI
from .routes import books, authRoute
from contextlib import asynccontextmanager
from src.db.main import init_db


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is starting ...")
    try:
        await init_db()
        yield
    finally:
        pass
    print("Server is shutting down...")


version = "v1"

app = FastAPI(
    version=version,
    title="Bookly",
    description="A simple book management system",
    lifespan=life_span,
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(books.router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(authRoute.router, prefix=f"/api/{version}/user", tags=["users"])
