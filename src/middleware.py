from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging
from src.config import Config

logger = logging.getLogger("uvicorn.access")
logger.disabled = True  # To disable logging


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        print("before", start_time)
        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f"{request.method}:{request.url.path} - {response.status_code} completed after {processing_time}"

        print("message:: ", message)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],
    )

    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     print("authorization: ", request.url.path)
    #     if request.url.path != "/redoc" and not "Authorization" in request.headers:
    #         return JSONResponse(
    #             status_code=401,
    #             content={
    #                 "message": "Authorization header is missing",
    #                 "resolution": "Please provide a valid token in authorization header",
    #             },
    #         )

    #     response = await call_next(request)
    #     return response
