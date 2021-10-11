"""
App response schemas
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from pydantic.main import BaseModel

JsonResponse = Dict[str, Any]


class GameLocation(BaseModel):
    area: str
    city: str
    country: str


class GameOwner(BaseModel):
    id: Union[str, int]
    name: str


class GameSearchResult(BaseModel):
    description: str
    images: list
    location: Optional[GameLocation]
    owner: Optional[GameOwner]
    prices: list
    source: str
    subject: str
    url: str


@dataclass
class APIResponse:
    response: JsonResponse
    status: int
