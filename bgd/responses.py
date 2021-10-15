"""
App response schemas
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from libbgg.infodict import InfoDict
from pydantic.main import BaseModel

JsonResponse = Dict[str, Any]


class GameLocation(BaseModel):
    area: str
    city: str
    country: str


class GameOwner(BaseModel):
    id: Union[str, int]
    name: str


class Price(BaseModel):
    byn: int
    usd: int


class GameSearchResult(BaseModel):
    description: str
    images: list
    location: Optional[GameLocation]
    owner: Optional[GameOwner]
    price: Optional[Price]
    source: str
    subject: str
    url: str


class GameRank(BaseModel):
    name: str
    value: str


class GameStatistic(BaseModel):
    avg_rate: str
    ranks: List[GameRank]


class GameDetailsResult(BaseModel):
    description: str
    id: str
    image: str
    max_play_time: str
    max_players: str
    min_play_time: str
    min_players: str
    name: str
    playing_time: str
    statistics: GameStatistic
    year_published: str


@dataclass
class APIResponse:
    response: Union[str, JsonResponse]
    status: int


@dataclass
class BGGAPIResponse:
    response: InfoDict
    status: int
