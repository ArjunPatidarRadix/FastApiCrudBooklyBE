"""
Tutorial reference : https://www.youtube.com/watch?v=TO4aQ3ghFOc
Documentation : https://jod35.github.io/fastapi-beyond-crud-docs/site/chapter5/
Git code: https://github.com/jod35/fastapi-beyond-CRUD/blob/main/src/__init__.py
"""

from fastapi import FastAPI

from .auth import authRoute
from .books import booksRoute
from .reviews import reviewsRoute
from contextlib import asynccontextmanager
from src.db.main import init_db
from fastapi.openapi.utils import get_openapi
from .errors import register_all_errors
from .middleware import register_middleware


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
    # lifespan=life_span,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Bookly API",
        version=version,
        description="A simple book management system with authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {"tokenUrl": f"/api/{version}/user/login", "scopes": {}}
            },
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

register_all_errors(app)

register_middleware(app)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(booksRoute.router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(authRoute.router, prefix=f"/api/{version}/user", tags=["users"])
app.include_router(
    reviewsRoute.router, prefix=f"/api/{version}/reviews", tags=["reviews"]
)


# fastapi dev src/main.py to run the server
