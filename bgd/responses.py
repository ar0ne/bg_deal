"""
App response schemas
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from pydantic.main import BaseModel

JsonResponse = Dict[str, Any]


class SearchLocation(BaseModel):
    area: str
    city: str
    country: str


class SearchOwner(BaseModel):
    id: Union[str, int]
    name: str
    phone: str


class SearchResponseItem(BaseModel):
    images: list
    location: Optional[SearchLocation]
    owner: Optional[SearchOwner]
    prices: list
    source: str
    url: str


@dataclass
class APIResponse:
    response: JsonResponse
    status: int
