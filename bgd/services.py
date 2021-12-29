"""
App Services
"""
import asyncio
import datetime
import json
import logging
import random
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, Tuple, Union

from bs4 import BeautifulSoup
from libbgg.infodict import InfoDict

from bgd.api_clients.builders import (
    CurrencyExchangeRateBuilder,
    GameDetailsResultBuilder,
    GameSearchResultBuilder,
)
from bgd.api_clients.protocols import (
    CurrencyExchangeRateSearcher,
    GameInfoSearcher,
    GameSearcher,
)
from bgd.api_clients.responses import JsonResponse
from bgd.api_clients.types import ExchangeRates, GameAlias
from bgd.errors import GameNotFoundError
from bgd.responses import GameDetailsResult, GameSearchResult, Price

log = logging.getLogger(__name__)


class GameInfoService(ABC):
    """Abstract game info service"""

    def __init__(
        self,
        client: GameInfoSearcher,
        builder: GameDetailsResultBuilder,
    ) -> None:
        """Init Search Service"""
        self._client = client
        self._game_result_builder = builder

    async def get_board_game_info(
        self, game: str, exact: bool = True
    ) -> GameDetailsResult:
        """Get board game info from API"""
        search_resp = await self._client.search_game_info(game, {"exact": exact})
        game_alias = self.get_game_alias(search_resp.response)
        if not game_alias:
            raise GameNotFoundError(game)
        game_info_resp = await self._client.get_game_details(game_alias)
        return self._game_result_builder.build(game_info_resp.response)

    @abstractmethod
    def get_game_alias(self, search_results: Any) -> Optional[GameAlias]:
        """Choose the best option from search results"""


class BoardGameGeekGameInfoService(GameInfoService):
    """Board Game Geek service"""

    def get_game_alias(self, search_results: InfoDict) -> Optional[GameAlias]:
        """
        Get game id from result of searching.
        Skip all games without year of publishing and take the newest one.
        """
        item = search_results.get("items").get("item")
        if not item:
            return None
        if not isinstance(item, list):
            return item["id"]

        def by_published_year(game_item: dict) -> int:
            """By published year"""
            if "yearpublished" not in game_item:
                return 0
            return int(game_item["yearpublished"]["value"])

        item.sort(key=by_published_year)
        # get the newest game
        return item[-1]["id"]


class TeseraGameInfoService(GameInfoService):
    """Game info service for tesera.ru"""

    def get_game_alias(self, search_results: JsonResponse) -> Optional[GameAlias]:
        """Choose the game from search response and returns alias"""
        # take first item in the list
        if len(search_results) and isinstance(search_results, list):
            return search_results[0]["alias"]
        return None


class CurrencyExchangeRateService:
    """Currency exchange rate service"""

    def __init__(
        self,
        client: CurrencyExchangeRateSearcher,
        rate_builder: CurrencyExchangeRateBuilder,
        base_currency: str,
        target_currency: str,
    ) -> None:
        """
        Init exchange rate service
        :param CurrencyExchangeRateSearcher client: A searcher of currency exchange rates.
        :param CurrencyExchangeRateBuilder rate_builder: Builder for ExchangeRates model.
        :param str base_currency: 3-letters currency code from which service does conversion.
        :param str target_currency: 3-letters currency code for conversion.
        """
        self._client = client
        self._builder = rate_builder
        self._target_currency = target_currency
        self._base_currency = base_currency
        self._rates: Optional[ExchangeRates] = None
        self._expiration_date: Optional[datetime.date] = None

    async def convert(self, price: Optional[Price]) -> Optional[Price]:
        """Convert amount to another currency"""
        if not price:
            return None
        rates = await self.get_rates()
        if not (rates and self._target_currency in rates):
            return None
        exchange_rate = rates[self._target_currency]
        return Price(
            amount=round(price.amount / exchange_rate),
            currency=self._target_currency,
        )

    async def get_rates(self) -> Optional[ExchangeRates]:
        """Get actual currency exchange rates"""
        today = datetime.date.today()
        if self._expiration_date and self._expiration_date <= today:
            self._rates = None
            self._expiration_date = None
        if not self._rates:
            # for safety let's use yesterday rates
            yesterday = today - datetime.timedelta(days=1)
            resp = await self._client.get_currency_exchange_rates(yesterday)
            self._rates = self._builder.from_response(resp.response)
            self._expiration_date = today + datetime.timedelta(days=1)
        return self._rates


class DataSource:
    """Abstract search service"""

    def __init__(
        self,
        client: GameSearcher,
        game_category_id: Union[str, int],
        result_builder: GameSearchResultBuilder,
        currency_exchange_rate_converter: CurrencyExchangeRateService,
    ) -> None:
        """Init Search Service"""
        self._client = client
        self._game_category_id = game_category_id
        self._result_builder = result_builder
        self._currency_converter = currency_exchange_rate_converter
        self._query = None

    @abstractmethod
    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        """search query"""

    def filter_results(
        self, products: list, filter_func: Optional[Callable] = None
    ) -> list:
        """Filter valid results"""
        if not products:
            return []
        if not filter_func:
            return products
        return list(filter(filter_func, products))

    async def search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Searching games"""
        log.info("Search data by: %s", self._client.__class__.__name__)
        self._query = query
        responses = await asyncio.gather(
            self.do_search(*args, **kwargs), return_exceptions=True
        )
        self._log_errors(responses)
        # filter exceptions
        results = list(filter(lambda r: r and isinstance(r, list), responses))
        # extract results if results is not empty
        search_results = results[0] if results else results
        # provide converted prices
        for result in search_results:  # type: ignore
            target_price = await self._currency_converter.convert(result.price)  # type: ignore
            result.price_converted = target_price  # type: ignore
        return search_results  # type: ignore

    def build_results(self, items: Optional[list]) -> List[GameSearchResult]:
        """prepare search results for end user"""
        if not (items and len(items)):
            return []
        return [self._result_builder.from_search_result(item) for item in items]

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


class KufarSearchService(DataSource):
    """Service for work with Kufar api"""

    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        """Search ads by game name"""
        search_response = await self._client.search(
            self._query, {"category": self._game_category_id}
        )
        products = self.filter_results(search_response.response["ads"])
        return self.build_results(products)


class WildberriesSearchService(DataSource):
    """Service for work with Wildberries api"""

    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        search_results = await self._client.search(self._query)
        products = self.filter_results(
            search_results.response["data"]["products"], self._is_available_game
        )
        return self.build_results(products)

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        return product.get("subjectId") == self._game_category_id


class OzonSearchService(DataSource):
    """Search Service for ozon api"""

    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(
            self._query, {"category": self._game_category_id, **kwargs}
        )
        results = self._extract_search_results(response.response)
        products = self.filter_results(results["items"])
        return self.build_results(products)

    def _extract_search_results(self, resp: dict) -> Optional[dict]:
        """Extract search results from response"""
        widget_states: dict = resp["widgetStates"]
        key = self._find_search_v2_key(widget_states)
        if not key:
            return None
        return json.loads(widget_states[key])

    @staticmethod
    def _find_search_v2_key(states: dict) -> Optional[str]:
        """Find a key in widget states"""
        for key in states.keys():
            if "searchResultsV2" in key:
                return key
        return None


class OzBySearchService(DataSource):
    """Search service for oz.by"""

    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(
            self._query, {"category": self._game_category_id, **kwargs}
        )
        products = self.filter_results(response.response["data"])
        return self.build_results(products)


class OnlinerSearchService(DataSource):
    """Search service for onliner.by"""

    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(self._query, **kwargs)
        products = self.filter_results(
            response.response["products"], self._is_available_game
        )
        return self.build_results(products)

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        return product["schema"]["key"] == "boardgame" and product["prices"]


class TwentyFirstVekSearchService(DataSource):
    """Search service for 21vek.by"""

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        return (
            product["type"] == "product"
            and product["price"] != "нет на складе"
            and "board_games" in product["url"]
        )

    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        """Search on api and build response"""
        response = await self._client.search(self._query, **kwargs)
        products = self.filter_results(
            response.response["items"], self._is_available_game
        )
        return self.build_results(products)


class FifthElementSearchService(DataSource):
    """Search service for 5element.by"""

    def __init__(
        self,
        client: GameSearcher,
        game_category_id: str,
        result_builder: GameSearchResultBuilder,
        search_app_id: str,
        currency_exchange_rate_converter: CurrencyExchangeRateService,
    ) -> None:
        """Init 5th element Search Service"""
        # there are more than one category that we should check
        self._game_category_ids = game_category_id.split(",")
        super().__init__(
            client, game_category_id, result_builder, currency_exchange_rate_converter
        )
        self._search_app_id = search_app_id

    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(
            self._query, {"search_app_id": self._search_app_id}
        )
        products = self.filter_results(
            response.response["results"]["items"], self._is_available_game
        )
        return self.build_results(products)

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        return (
            product["is_presence"]
            and product["params_data"]["category_id"] in self._game_category_ids
        )


class VkontakteSearchService(DataSource):
    """Search service for vk.com"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        client: GameSearcher,
        game_category_id: str,
        result_builder: GameSearchResultBuilder,
        api_version: str,
        api_token: str,
        group_id: str,
        group_name: str,
        limit: int,
        currency_exchange_rate_converter: CurrencyExchangeRateService,
    ) -> None:
        """Init 5th element Search Service"""
        # there are more than one category that we should check
        super().__init__(
            client, game_category_id, result_builder, currency_exchange_rate_converter
        )
        self.api_version = api_version
        self.api_token = api_token
        self.group_id = group_id
        self.group_name = group_name
        self.limit = limit

    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        search_response = await self._client.search(
            self._query,
            {
                "api_token": self.api_token,
                "api_version": self.api_version,
                "group_id": self.group_id,
                "limit": self.limit,
            },
        )
        products = self.filter_results(
            search_response.response["response"]["items"], self._is_available_game
        )
        return self.build_results(products)

    def _is_available_game(self, product: dict, query: str) -> bool:
        """True if it's available board game"""
        # @todo: is it possible to do it better?  # typing: disable=fixme
        return re.search(query, product["text"], re.IGNORECASE)  # type: ignore

    def filter_results(
        self, products: list, filter_func: Optional[Callable] = None
    ) -> list:
        """Filter only valid results"""
        return [product for product in products if filter_func(product, self._query)]


class SuggestGameService:
    """Suggest game service"""

    def __init__(self, games: str) -> None:
        """Init service"""
        self.games = [game.strip() for game in games.split(",")]

    async def suggest(self) -> str:
        """Suggest random game from the list"""
        return random.choice(self.games)


class ZnaemIgraemSearchService(DataSource):
    """Search service for znaemigraem.by"""

    def _is_available_game(self, product: dict) -> bool:
        """True if game is available for purchase"""
        return product["available"]

    async def do_search(self, *args, **kwargs) -> List[GameSearchResult]:
        """Search query"""
        html_page = await self._client.search(self._query)
        # find products on search page
        soup = BeautifulSoup(html_page.response, "html.parser")

        search_results = soup.find(class_="c-search__results")
        items = search_results.find_all(class_="catalog-item")
        products = []
        for item in items:
            # filter unavailable products
            if item.find(class_="catalog-item__amount").find("span"):
                continue
            product = {
                "image": item.find("img")["src"],
                "name": item.find(class_="name").get_text(),
                "price": item.find(class_="catalog-item__price").get_text(),
                "url": item.find(class_="image")["href"],
            }
            products.append(product)

        return self.build_results(products)
