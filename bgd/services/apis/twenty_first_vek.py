"""
21.vek API Client
"""
from typing import List, Optional

from bgd.responses import GameSearchResult
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.protocols import JsonHttpApiClient
from bgd.services.responses import APIResponse


class TwentyFirstVekApiClient(JsonHttpApiClient):
    """Api client for 21vek.by"""

    BASE_SEARCH_URL = "https://search.21vek.by/api/v1.0"
    SEARCH_PATH = "/search/suggest"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search by query string"""
        url = f"{self.SEARCH_PATH}?q={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class TwentyFirstVekSearchService(GameSearchService):
    """Search service for 21vek.by"""

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        return (
            product["type"] == "product"
            and product["price"] != "нет на складе"
            and "board_games" in product["url"]
        )

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Search on api and build response"""
        response = await self._client.search(query, **kwargs)
        products = self.filter_results(
            response.response["items"], self._is_available_game
        )
        return self.build_results(products)
