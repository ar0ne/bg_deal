"""
Application entrypoint
"""
import os

from fastapi import FastAPI

from bgd import endpoints
from bgd.containers import ApplicationContainer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app() -> FastAPI:
    """Create application"""

    container = ApplicationContainer()
    container.config.from_yaml(f"{BASE_DIR}/config.yml")
    container.wire(modules=[endpoints])

    app = FastAPI()
    app.container = container  # type: ignore
    app.include_router(endpoints.router)

    return app


app = create_app()
