"""
App Errors
"""
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from starlette_json import ORJsonResponse

# pylint: disable=super-init-not-called, fixme


# TODO: refactor exceptions
class ServiceException(Exception):
    """Generic Service Exception class"""

    def __init__(self, error: str, message: str = "") -> None:
        """Init"""
        super().__init__()
        self.error = error
        self.message = message


class ApiClientError(ServiceException):
    """Api Error exception"""

    def __init__(self, message: str) -> None:
        """init"""
        self.error = "api_client"
        self.message = f"Api Client Error: status = {message}"


class PageNotFoundError(ApiClientError):
    """Page not found Api Client Error"""

    def __init__(self, url: str) -> None:
        """Init"""
        self.error = "api_client"
        self.message = f"Page Not Found: {url}"


# pylint: disable=unused-argument
async def service_exception_handler(_: Request, exc: ServiceException) -> Response:
    """Handler for service exceptions"""
    return ORJsonResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.error, "message": exc.message},
    )


class GameNotFoundError(ServiceException):
    """Game Not Found Error"""

    def __init__(self, game_name: str) -> None:
        """init"""
        self.error = "game_not_found"
        self.message = f"Game '{game_name}' is not found!"
