"""
Client responses
"""
from dataclasses import asdict, dataclass
from typing import Any, Optional

from libbgg.infodict import InfoDict

from bgd.api_clients.types import JsonResponse


@dataclass
class APIResponse:
    """API Response"""

    response: Any
    status: int


@dataclass
class JSONAPIResponse(APIResponse):
    """API Response class"""

    response: JsonResponse
    status: int


@dataclass
class XMLAPIResponse(APIResponse):
    """XML Api Response model"""

    response: InfoDict
    status: int


@dataclass
class HTMLAPIResponse(APIResponse):
    """Html API Resource"""

    response: str
    status: int


@dataclass
class APIRequest:
    """API request model"""

    method: str
    url: str
    headers: dict
    json: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
