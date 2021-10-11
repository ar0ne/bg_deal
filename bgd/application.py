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

    app = FastAPI()
    app.container = container  # type: ignore
    app.exception_handler(ServiceException)(errors.service_exception_handler)
    app.include_router(endpoints.router)

    logging.config.fileConfig(
        f"{BASE_DIR}/logging.conf", disable_existing_loggers=False
    )

    app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")

    return app


app = create_app()
