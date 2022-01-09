"""
App builders
"""
from typing import Any, Optional, Protocol

from bgd.constants import USD
from bgd.responses import GameDetailsResult, GameSearchResult, Price
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


class SuggestGameService(Protocol):
    """Suggest game service interface"""

    async def suggest(self) -> str:
        """Suggest a game"""
        ...


class CurrencyExchangeRateService(Protocol):
    """Currency exchange rate service interface"""

    async def convert(self, price: Optional[Price], target_currency: str = USD) -> Optional[Price]:
        """Convert price to another currency"""
        ...

    async def get_rates(self) -> Optional[ExchangeRates]:
        """Get actual currency exchange rates"""
        ...
