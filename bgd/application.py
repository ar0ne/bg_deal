"""
Application entrypoint
"""
import logging
import os

from dependency_injector.wiring import Provide, inject, required
from environ import Env
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends import Backend
from starlette_json import ORJsonMiddleware

from bgd import endpoints, errors
from bgd.containers import ApplicationContainer
from bgd.errors import ServiceException

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app() -> FastAPI:
    """Create application"""
    env = Env()
    env.read_env(f"{BASE_DIR}/.env")

    container = ApplicationContainer()
    container.config.from_yaml(f"{BASE_DIR}/config.yml", envs_required=True)
    container.wire(modules=[".application", ".endpoints"])

    fast_api_app = FastAPI()
    fast_api_app.container = container  # type: ignore
    fast_api_app.exception_handler(ServiceException)(errors.service_exception_handler)
    fast_api_app.include_router(endpoints.router)

    logging.config.fileConfig(  # type: ignore
        f"{BASE_DIR}/logging.conf", disable_existing_loggers=False
    )

    fast_api_app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")

    return fast_api_app


@inject
def startup_event(
    cache_backend: Backend = Provide[ApplicationContainer.cache_backend],
    cache_prefix: str = Provide["config.cache.prefix", required()],
    cache_ttl: int = Provide["config.cache.ttl", required().as_int()],
) -> None:
    """On startup callback"""
    FastAPICache.init(cache_backend, prefix=cache_prefix, expire=cache_ttl)


app = create_app()
app.add_event_handler("startup", startup_event)
app.add_middleware(ORJsonMiddleware)
