"""
App builders
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol

from bgd.responses import GameDetailsResult, GameSearchResult

from .types import ExchangeRates


class GameDetailsResultFactory(Protocol):
    """Abstract GameDetailsResultBuilder class"""

    def create(self, game_info: Any) -> GameDetailsResult:
        """Create game details result"""
        ...


class GameSearchResultBuilder(ABC):
    """Base builder class for game search result"""

    @classmethod
    @abstractmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Build game search result from search result"""


class CurrencyExchangeRateBuilder(ABC):
    """Interface for builders of currency exchange rates"""

    @staticmethod
    @abstractmethod
    def from_response(response: Any) -> Optional[ExchangeRates]:
        """Build exchange rates from response"""
        ...
