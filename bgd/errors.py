"""
App Errors
"""
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse


class ServiceException(Exception):
    def __init__(self, error: str, message: str = "") -> None:
        self.error = error
        self.message = message


class ApiClientError(ServiceException):
    """Api Error exception"""

    def __init__(self, message: str) -> None:
        self.error = "api_client"
        self.message = f"Api Client Error: status = {message}"


class NotFoundApiClientError(ApiClientError):
    """Page not found Api Client Error"""

    def __init__(self, url: str) -> None:
        self.error = "api_client"
        self.message = f"Page Not Found: {url}"


async def service_exception_handler(
    request: Request, exc: ServiceException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": exc.error, "message": exc.message},
    )
