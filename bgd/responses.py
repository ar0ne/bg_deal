"""
App response schemas
"""
from typing import List, Optional, Union

from pydantic.main import BaseModel  # pylint: disable=no-name-in-module

from bgd.constants import BYN


class GameLocation(BaseModel):
    """Game location model"""

    area: str
    city: str
    country: str


class GameOwner(BaseModel):
    """Owner of the game e.g. if it's auction"""

    id: Union[str, int]
    name: str
    url: Optional[str]


class Price(BaseModel):
    """Price model"""

    amount: int
    currency: str = BYN


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
    price_converted: Optional[Price] = None


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

    best_num_players: Optional[str]
    bgg_id: str
    bgg_url: str
    description: str
    id: str
    image: str
    max_play_time: str
    max_players: str
    min_play_time: str
    min_players: str
    name: str
    playing_time: str
    source: str
    statistics: GameStatistic
    url: str
    year_published: str
