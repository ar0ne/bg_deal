"""
App Services
"""
import asyncio
import json
import logging
from abc import abstractmethod
from typing import Any, List, Optional, Tuple, Union

from bgd.builders import GameDetailsResultBuilder, GameSearchResultBuilder
from bgd.clients import ApiClient, BoardGameGeekApiClient
from bgd.errors import GameNotFoundError
from bgd.responses import (
    BGGAPIResponse,
    GameDetailsResult,
    GameSearchResult,
    JsonResponse,
)

log = logging.getLogger(__name__)


class BoardGameGeekService:
    """Board Game Geek service"""

    def __init__(self, client: BoardGameGeekApiClient) -> None:
        """Init Search Service"""
        self._client = client

    async def get_board_game_info(self, game_name: str) -> GameDetailsResult:
        """Get info about board game"""
        search_resp = await self._client.search_game(game_name)
        game_id = self._get_game_id_from_search_result(search_resp)
        if not game_id:
            raise GameNotFoundError(game_name)
        game_info_resp = await self._client.get_thing_by_id(game_id)
        return GameDetailsResultBuilder.from_game_info(game_info_resp.response)

    @staticmethod
    def _get_game_id_from_search_result(search_resp: BGGAPIResponse) -> Optional[str]:
        """
        Get game id from result of searching.
        Skip all games without year of publishing and take the newest one.
        """
        item = search_resp.response.get("items").get("item")
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


class DataSource:
    """Abstract search service"""

    def __init__(
        self,
        client: ApiClient,
        game_category_id: Union[str, int],
        result_builder: GameSearchResultBuilder,
    ) -> None:
        """Init Search Service"""
        self._client = client
        self.game_category_id = game_category_id
        self.result_builder = result_builder

    @abstractmethod
    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """search query"""

    @abstractmethod
    def filter_results(self, response: JsonResponse) -> list:
        """Filter valid results"""

    async def search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Searching games"""
        responses = await asyncio.gather(
            self.do_search(query, *args, **kwargs), return_exceptions=True
        )
        self._log_errors(responses)
        # filter exceptions
        results = list(filter(lambda res: res and isinstance(res, list), responses))
        # extract results if results is not empty
        return results[0] if results else results  # type: ignore

    def build_results(self, items: Optional[list]) -> List[GameSearchResult]:
        """prepare search results for end user"""
        if not (items and len(items)):
            return []
        return [self.result_builder.from_search_result(item) for item in items]

    @staticmethod
    def _log_errors(all_responses: Tuple[Union[Any, Exception]]):
        """Log errors if any occur"""
        for resp in all_responses:
            if not isinstance(resp, list):
                log.warning("Error appeared during searching: %s", resp, exc_info=True)


class KufarSearchService(DataSource):
    """Service for work with Kufar api"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Search ads by game name"""
        search_response = await self._client.search(
            query, {"category": self.game_category_id}
        )
        products = self.filter_results(search_response.response)
        return self.build_results(products)

    def filter_results(self, response: JsonResponse) -> list:
        """Filter only valid results"""
        return response["ads"]


class WildberriesSearchService(DataSource):
    """Service for work with Wildberries api"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        search_results = await self._client.search(query)
        products = self.filter_results(search_results.response)
        return self.build_results(products)

    def filter_results(self, response: JsonResponse) -> list:
        """Filter only valid results"""
        return list(
            filter(
                lambda pr: pr.get("subjectId") == self.game_category_id,
                response["data"]["products"],
            )
        )


class OzonSearchService(DataSource):
    """Search Service for ozon api"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(
            query, {"category": self.game_category_id, **kwargs}
        )
        products = self.filter_results(response.response)
        return self.build_results(products)

    def filter_results(self, response: JsonResponse) -> list:
        search_results = self._extract_search_results(response)
        if not search_results:
            return []
        return search_results["items"]

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

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(
            query, {"category": self.game_category_id, **kwargs}
        )
        products = self.filter_results(response.response)
        return self.build_results(products)

    def filter_results(self, response: JsonResponse) -> list:
        """Filter valid results"""
        return response["data"]


class OnlinerSearchService(DataSource):
    """Search service for onliner.by"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(query, **kwargs)
        products = self.filter_results(response.response)
        return self.build_results(products)

    def filter_results(self, response: JsonResponse) -> list:
        """Filter valid results"""
        # exclude non boardgames from the result and games without prices
        products = response["products"]
        if not products:
            return []
        return [
            product
            for product in products
            if product["schema"]["key"] == "boardgame" and product["prices"]
        ]


class TwentyFirstVekSearchService(DataSource):
    """Search service for 21vek.by"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Search on api and build response"""
        response = await self._client.search(query, **kwargs)
        products = self.filter_results(response.response)
        return self.build_results(products)

    def filter_results(self, response: JsonResponse) -> list:
        """Filter only valid results"""
        products = response["items"]
        if not products:
            return []
        # exclude non board games and not available products from response
        return [
            product
            for product in products
            if product["type"] == "product"
            and product["price"] != "нет на складе"
            and "board_games" in product["url"]
        ]


class FifthElementSearchService(DataSource):
    """Search service for 5element.by"""

    def __init__(
        self,
        client: ApiClient,
        game_category_id: str,
        result_builder: GameSearchResultBuilder,
        search_app_id: str,
    ) -> None:
        """Init 5th element Search Service"""
        # there are more than one category that we should check
        self.game_category_ids = game_category_id.split(",")
        super().__init__(client, game_category_id, result_builder)
        self.search_app_id = search_app_id

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(
            query, {"search_app_id": self.search_app_id}
        )
        products = self.filter_results(response.response)
        return self.build_results(products)

    def filter_results(self, response: JsonResponse) -> list:
        """Filter only valid results"""
        products = response["results"]["items"]
        if not products:
            return []
        # exclude non table and not available top boardgames from results
        return [
            product
            for product in products
            if product["is_presence"]
            and product["params_data"]["category_id"] in self.game_category_ids
        ]
