"""
App Services
"""
import asyncio
import collections
import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Callable, List, Optional, Sequence, Tuple, Union

from fastapi_cache import Coder
from fastapi_cache.decorator import cache
from starlette.requests import Request

from bgd.constants import BYN, RUB, USD
from bgd.errors import GameNotFoundError
from bgd.responses import GameDetailsResult, GameSearchResult
from bgd.services.abc import (
    CurrencyExchangeRateService,
    GameDetailsResultFactory,
    GameSearchResultFactory,
)
from bgd.services.api_clients import GameInfoSearcher, GameSearcher
from bgd.services.types import GameAlias

log = logging.getLogger(__name__)

STREAM_RETRY_TIMEOUT = 600  # milliseconds


class GameInfoService(ABC):
    """Abstract game info service"""

    def __init__(self, client: GameInfoSearcher, result_factory: GameDetailsResultFactory) -> None:
        """Init Search Service"""
        self._client = client
        self._result_factory = result_factory

    async def get_board_game_info(self, game: str, exact: bool = True) -> GameDetailsResult:
        """Get board game info from API"""
        search_resp = await self._client.search_game_info(game, {"exact": exact})
        game_alias = self.get_game_alias(search_resp.response)
        if not game_alias:
            raise GameNotFoundError(game)
        game_info_resp = await self._client.get_game_details(game_alias)
        return self._result_factory.create(game_info_resp.response)

    @abstractmethod
    def get_game_alias(self, search_results: Any) -> Optional[GameAlias]:
        """Choose the best option from search results"""


class GameSearchService(ABC):
    """Abstract search service"""

    def __init__(
        self,
        client: GameSearcher,
        result_factory: GameSearchResultFactory,
        currency_exchange_rate_converter: CurrencyExchangeRateService,
        game_category_id: Optional[Union[str, int]] = None,
    ) -> None:
        """Init Search Service"""
        self._client = client
        self._result_factory = result_factory
        self._game_category_id = game_category_id
        self._currency_converter = currency_exchange_rate_converter

    @abstractmethod
    async def do_search(self, query: str, *args, **kwargs) -> Tuple[GameSearchResult]:
        """search query"""

    def filter_results(
        self, products: Sequence, filter_func: Optional[Callable] = None
    ) -> Sequence:
        """Filter valid results"""
        if not products:
            return ()
        if not filter_func:
            return products
        return tuple(filter(filter_func, products))

    @cache()
    async def search(self, query: str, *args, **kwargs) -> Sequence[dict]:
        """Searches a game by query"""
        log.info("Search data by: %s", self._client.__class__.__name__)
        responses = await asyncio.gather(
            self.do_search(query, *args, **kwargs), return_exceptions=True
        )
        # filter out non errors
        search_results = self.cleanup_responses(responses)
        # add prices in different currencies
        search_results_priced = [await self.convert_price(result) for result in search_results]
        # convert from dto to dicts, to make possible to cache it
        return tuple(res.dict() for res in search_results_priced)

    def build_results(self, items: Optional[Sequence[dict]]) -> Tuple[GameSearchResult]:
        """prepare search results for end user"""
        if not items:
            return ()  # type: ignore
        return tuple(map(self._result_factory.create, items))  # type: ignore

    def cleanup_responses(
        self, all_responses: Tuple[Union[Any, Exception]]
    ) -> Tuple[GameSearchResult]:
        """Filter responses and log errors if any occur"""
        cleared_responses = []
        for resp in all_responses:
            if isinstance(resp, collections.abc.Sequence):
                cleared_responses.append(resp)
            else:
                log.warning(
                    "Error appeared during searching: %s in %s",
                    resp,
                    self._client.__class__.__name__,
                    exc_info=True,
                )
        # extract results if results is not empty
        return cleared_responses[0] if cleared_responses else cleared_responses  # type: ignore

    async def convert_price(self, result: GameSearchResult) -> GameSearchResult:
        """Add price in different currencies"""
        if not result.prices:
            return result
        base_price = result.prices[0]
        if base_price.currency == BYN:
            price_in_usd = await self._currency_converter.convert(base_price, USD)
            if not price_in_usd:
                return result
            result.prices.append(price_in_usd)
        elif base_price.currency == RUB:
            price_in_byn = await self._currency_converter.convert(base_price, BYN)
            if not price_in_byn:
                return result
            result.prices.append(price_in_byn)
            price_in_usd = await self._currency_converter.convert(price_in_byn, USD)
            if price_in_usd:
                result.prices.append(price_in_usd)
        return result


class SimpleSuggestGameService:
    """Suggest game service"""

    def __init__(self, games: str) -> None:
        """Init service"""
        self.games = tuple(game.strip() for game in games.split(","))

    async def suggest(self) -> str:
        """Suggest random game from the list"""
        return random.choice(self.games)


class GameDealsSearchFacade:
    """Facade for game search logic"""

    def __init__(self, data_sources: List[GameSearchService], json_coder: Coder) -> None:
        """Init game search facade"""
        self.data_sources = data_sources
        self.json_coder = json_coder

    def serialize_event_data(self, data: Any) -> str:
        """Convert event data to JSON-string"""
        return self.json_coder.encode(data)  # pylint: disable=no-member

    async def find_game_deals(self, request: Request, game: str) -> AsyncGenerator[dict, None]:
        """Async game deals searching"""
        start = time.time()
        while True:
            if await request.is_disconnected():
                log.debug("Request disconnected.")
                break

            for source in self.data_sources:
                deals = await source.search(game)
                if deals:
                    yield {
                        "event": "update",
                        "retry": STREAM_RETRY_TIMEOUT,
                        # convert to json-string for frontend
                        "data": self.serialize_event_data(deals),
                    }

            log.debug("We processed all data sources. Close connection.")
            elapsed_time = f"{time.time() - start:.2f}"
            yield {
                "event": "end",
                "data": self.serialize_event_data(
                    {
                        "time": elapsed_time,
                    }
                ),
            }
            break
