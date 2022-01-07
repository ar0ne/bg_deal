"""
App builders
"""
from typing import Any, Optional, Protocol

from bgd.responses import GameDetailsResult, GameSearchResult
from bgd.services.types import ExchangeRates


class GameDetailsResultFactory(Protocol):
    """Abstract GameDetailsResultBuilder class"""

    def create(self, game_info: Any) -> GameDetailsResult:
        """Create game details result"""
        ...


class GameSearchResultFactory(Protocol):
    """Game search result factory"""

    def create(self, search_result: dict) -> GameSearchResult:
        """Build game search result from search result"""
        ...


class CurrencyExchangeRateFactory(Protocol):
    """Interface for currency exchange rates"""

    def create(self, response: Any) -> Optional[ExchangeRates]:
        """Creates exchange rates from response"""
        ...
