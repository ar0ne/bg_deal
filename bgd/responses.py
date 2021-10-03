"""
App response schemas
"""
from typing import Union

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
    location: SearchLocation
    owner: SearchOwner
    prices: list
    url: str
