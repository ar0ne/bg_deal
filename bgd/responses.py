"""
App response schemas
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from libbgg.infodict import InfoDict
from pydantic.main import BaseModel  # pylint: disable=no-name-in-module

JsonResponse = Dict[str, Any]


class GameLocation(BaseModel):
    """Game location model"""

    area: str
    city: str
    country: str


class GameOwner(BaseModel):
    """Owner of the game e.g. if it's auction"""

    id: Union[str, int]
    name: str


class Price(BaseModel):
    """Price model"""

    byn: int
    usd: int


class GameSearchResult(BaseModel):
    """Search result model"""

    description: str
    images: list
    location: Optional[GameLocation]
    owner: Optional[GameOwner]
    price: Optional[Price]
    source: str
    subject: str
    url: str


class GameRank(BaseModel):
    """Game rank mode"""

    name: str
    value: str


class GameStatistic(BaseModel):
    """Game statistics model"""

    avg_rate: str
    ranks: List[GameRank]
    weight: str


class GameDetailsResult(BaseModel):
    """Game details result model"""

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
    url: str
    year_published: str


@dataclass
class APIResponse:
    """API Response class"""

    response: JsonResponse
    status: int


@dataclass
class BGGAPIResponse:
    """BGG Api Response model"""

    response: InfoDict
    status: int
