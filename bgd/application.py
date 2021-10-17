"""
Application entrypoint
"""
import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from bgd import endpoints, errors
from bgd.containers import ApplicationContainer
from bgd.errors import ServiceException

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app() -> FastAPI:
    """Create application"""

    container = ApplicationContainer()
    container.config.from_yaml(f"{BASE_DIR}/config.yml")
    container.wire(modules=[endpoints])

    fast_api_app = FastAPI()
    fast_api_app.container = container  # type: ignore
    fast_api_app.exception_handler(ServiceException)(errors.service_exception_handler)
    fast_api_app.include_router(endpoints.router)

    logging.config.fileConfig(  # type: ignore
        f"{BASE_DIR}/logging.conf", disable_existing_loggers=False
    )

    fast_api_app.mount(
        "/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static"
    )

    return fast_api_app


app = create_app()
