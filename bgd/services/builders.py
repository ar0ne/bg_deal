"""
App builders
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol

from bgd.responses import GameDetailsResult, GameSearchResult

from .types import ExchangeRates


class GameDetailsResultBuilder(ABC):
    """Abstract GameDetailsResultBuilder class"""

    @classmethod
    @abstractmethod
    def build(cls, game_info: Any) -> GameDetailsResult:
        """Build game details result"""


class GameSearchResultBuilder:
    """Base builder class for game search result"""

    @classmethod
    @abstractmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Build game search result from search result"""


class CurrencyExchangeRateBuilder(Protocol):
    """Interface for builders of currency exchange rates"""

    @staticmethod
    def from_response(response: Any) -> Optional[ExchangeRates]:
        """Build exchange rates from response"""
        ...
