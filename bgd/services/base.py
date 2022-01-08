"""
App Services
"""
import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, Protocol, Tuple, Union

from fastapi_cache.decorator import cache

from bgd.errors import GameNotFoundError
from bgd.responses import GameDetailsResult, GameSearchResult, Price
from bgd.services.abc import GameDetailsResultFactory, GameSearchResultFactory
from bgd.services.api_clients import GameInfoSearcher, GameSearcher
from bgd.services.types import ExchangeRates, GameAlias

log = logging.getLogger(__name__)


class GameInfoService(ABC):
    """Abstract game info service"""

    def __init__(self, client: GameInfoSearcher) -> None:
        """Init Search Service"""
        self._client = client

    async def get_board_game_info(self, game: str, exact: bool = True) -> GameDetailsResult:
        """Get board game info from API"""
        search_resp = await self._client.search_game_info(game, {"exact": exact})
        game_alias = self.get_game_alias(search_resp.response)
        if not game_alias:
            raise GameNotFoundError(game)
        game_info_resp = await self._client.get_game_details(game_alias)
        return self.result_factory.create(game_info_resp.response)

    @abstractmethod
    def get_game_alias(self, search_results: Any) -> Optional[GameAlias]:
        """Choose the best option from search results"""

    @property
    @abstractmethod
    def result_factory(self) -> GameDetailsResultFactory:
        """Get game details result factory"""


class CurrencyExchangeRateService(Protocol):
    """Currency exchange rate service interface"""

    async def convert(self, price: Optional[Price]) -> Optional[Price]:
        """Convert price to another currency"""
        ...

    async def get_rates(self) -> Optional[ExchangeRates]:
        """Get actual currency exchange rates"""
        ...


class GameSearchService(ABC):
    """Abstract search service"""

    def __init__(
        self,
        client: GameSearcher,
        currency_exchange_rate_converter: CurrencyExchangeRateService,
        game_category_id: Optional[Union[str, int]] = None,
    ) -> None:
        """Init Search Service"""
        self._client = client
        self._game_category_id = game_category_id
        self._currency_converter = currency_exchange_rate_converter

    @abstractmethod
    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """search query"""

    def filter_results(self, products: list, filter_func: Optional[Callable] = None) -> list:
        """Filter valid results"""
        if not products:
            return []
        if not filter_func:
            return products
        return list(filter(filter_func, products))

    @cache()
    async def search(self, query: str, *args, **kwargs) -> List[dict]:
        """Searching games"""
        log.info("Search data by: %s", self._client.__class__.__name__)
        responses = await asyncio.gather(
            self.do_search(query, *args, **kwargs), return_exceptions=True
        )
        self._log_errors(responses)
        # filter exceptions
        results = list(filter(lambda r: r and isinstance(r, list), responses))
        # extract results if results is not empty
        search_results = results[0] if results else results
        # add converted prices
        await self.prepare_prices(search_results)
        # convert from dto to dicts, to make possible to cache it
        return list(map(lambda s: s.dict(), search_results))  # type: ignore

    def build_results(self, items: Optional[list]) -> List[GameSearchResult]:
        """prepare search results for end user"""
        if not (items and len(items)):
            return []
        return list(map(self.result_factory.create, items))

    def _log_errors(self, all_responses: Tuple[Union[Any, Exception]]) -> None:
        """Log errors if any occur"""
        for resp in all_responses:
            if not isinstance(resp, list):
                log.warning(
                    "Error appeared during searching: %s in %s",
                    resp,
                    self._client.__class__.__name__,
                    exc_info=True,
                )

    async def prepare_prices(self, search_results: List[GameSearchResult]) -> None:
        """prepare prices for rendering"""
        # provide converted prices
        for result in search_results:  # type: ignore
            if not result.price:
                continue
            target_price = await self._currency_converter.convert(result.price)  # type: ignore
            result.price_converted = target_price  # type: ignore
            result.price.amount /= 100
            result.price_converted.amount /= 100

    @property
    @abstractmethod
    def result_factory(self) -> GameSearchResultFactory:
        """Get game search result factory"""


class SuggestGameService(ABC):
    """Suggest game service interface"""

    @abstractmethod
    async def suggest(self) -> str:
        """Suggest a game"""


class SimpleSuggestGameService(SuggestGameService):
    """Suggest game service"""

    def __init__(self, games: str) -> None:
        """Init service"""
        self.games = [game.strip() for game in games.split(",")]

    async def suggest(self) -> str:
        """Suggest random game from the list"""
        return random.choice(self.games)
