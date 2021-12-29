"""
Oz.by API Client
"""
from typing import List, Optional

from bgd.responses import GameSearchResult
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.protocols import JsonHttpApiClient
from bgd.services.responses import APIResponse


class OzByApiClient(JsonHttpApiClient):
    """Api client for Oz.by"""

    BASE_SEARCH_URL = "https://api.oz.by"
    SEARCH_PATH = "/v4/search"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search items by query"""
        category = options["category"]  # type: ignore
        url = (
            f"{self.SEARCH_PATH}?fieldsets[goods]=listing&"
            f"filter[id_catalog]={category}"
            f"&filter[availability]=1&filter[q]={query}"
        )
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class OzBySearchService(GameSearchService):
    """Search service for oz.by"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(
            query, {"category": self._game_category_id, **kwargs}
        )
        products = self.filter_results(response.response["data"])
        return self.build_results(products)
