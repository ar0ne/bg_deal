"""
Onliner (catalog) API Client
"""
from typing import List, Optional

from bgd.responses import GameSearchResult
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.protocols import JsonHttpApiClient
from bgd.services.responses import APIResponse


class OnlinerApiClient(JsonHttpApiClient):
    """Api client for onliner.by"""

    BASE_SEARCH_URL = "https://catalog.onliner.by/sdapi"
    SEARCH_PATH = "/catalog.api/search/products"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search by query string"""
        url = f"{self.SEARCH_PATH}?query={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class OnlinerSearchService(GameSearchService):
    """Search service for onliner.by"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(query, **kwargs)
        products = self.filter_results(
            response.response["products"], self._is_available_game
        )
        return self.build_results(products)

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        return product["schema"]["key"] == "boardgame" and product["prices"]
