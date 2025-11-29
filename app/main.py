from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from app.core.cache import lifespan_redis
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    async with lifespan_redis():
        yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="0.1.0",
        lifespan=lifespan,
    )

    if settings.cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.cors_origins],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()

