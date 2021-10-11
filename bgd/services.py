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
from bgd.responses import BGGAPIResponse, GameDetailsResult, GameSearchResult

log = logging.getLogger(__name__)


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

    async def search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Searching games"""
        responses = await asyncio.gather(
            self.do_search(query, *args, **kwargs), return_exceptions=True
        )
        self._log_errors(responses)
        # filter BaseExceptions
        ret: List[GameSearchResult] = [
            resp for resp in responses if isinstance(resp, list) and len(resp)
        ]
        return ret[0] if ret else ret

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
                log.warning("Error appeared during searching: %s", resp)


class KufarSearchService(DataSource):
    """Service for work with Kufar api"""

    async def do_search(
        self, game_name: str, *args, **kwargs
    ) -> List[GameSearchResult]:
        """Search ads by game name"""
        search_response = await self._client.search(
            game_name, {"category": self.game_category_id}
        )
        return self.build_results(search_response.response.get("ads"))


class WildberriesSearchService(DataSource):
    """Service for work with Wildberries api"""

    async def do_search(
        self, game_name: str, *args, **kwargs
    ) -> List[GameSearchResult]:
        search_results = await self._client.search(game_name)
        products = list(
            filter(
                lambda pr: pr.get("subjectId") == self.game_category_id,
                search_results.response.get("data", {}).get("products"),
            )
        )
        return self.build_results(products)


class OzonSearchService(DataSource):
    """Search Service for ozon api"""

    async def do_search(
        self, game_name: str, *args, **kwargs
    ) -> List[GameSearchResult]:
        response = await self._client.search(
            game_name, {"category": self.game_category_id, **kwargs}
        )
        search_results = self._extract_search_results(response.response)
        return self.build_results(search_results.get("items"))

    def _extract_search_results(self, resp: dict) -> Optional[dict]:
        """Extract search results from response"""
        widget_states = resp.get("widgetStates", {})
        key = self._find_search_v2_key(widget_states)
        return json.loads(widget_states.get(key, "{}"))

    @staticmethod
    def _find_search_v2_key(states: dict) -> Optional[str]:
        """Find a key in widget states"""
        for key in states.keys():
            if "searchResultsV2" in key:
                return key


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
    def _get_game_id_from_search_result(search_resp: BGGAPIResponse) -> str:
        """Get game id from result of searching"""
        return search_resp.response.get("items", {}).get("item", {}).get("id")
