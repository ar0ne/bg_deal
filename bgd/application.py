"""
Application entrypoint
"""
from fastapi import FastAPI

from bgd import endpoints
from bgd.containers import Container


def create_app() -> FastAPI:
    """Create application"""

    container = Container()
    container.wire(modules=[endpoints])

    app = FastAPI()
    app.container = container
    app.include_router(endpoints.router)

    return app


app = create_app()
