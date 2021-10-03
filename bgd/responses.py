"""
App response schemas
"""
from typing import Optional, Union

from pydantic.main import BaseModel


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
