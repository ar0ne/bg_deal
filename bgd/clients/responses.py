"""
Client responses
"""
from dataclasses import dataclass
from typing import Any, Dict

from libbgg.infodict import InfoDict

JsonResponse = Dict[str, Any]


@dataclass
class APIResponse:
    """API Response class"""

    response: JsonResponse
    status: int


@dataclass
class BGGAPIResponse(APIResponse):
    """BGG Api Response model"""

    response: InfoDict
    status: int
