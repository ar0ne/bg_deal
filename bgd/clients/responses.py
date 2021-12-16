"""
Client responses
"""
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from libbgg.infodict import InfoDict

JsonResponse = Dict[str, Any]


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
    """BGG Api Response model"""

    response: InfoDict
    status: int


@dataclass
class APIRequest:
    method: str
    url: str
    headers: dict
    json: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
