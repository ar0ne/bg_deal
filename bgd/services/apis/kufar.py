"""
Kufar.by API Client
"""
from typing import List, Optional

from bgd.responses import GameSearchResult
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.protocols import JsonHttpApiClient
from bgd.services.responses import APIResponse


class KufarApiClient(JsonHttpApiClient):
    """Client for Kufar API"""

    BASE_URL = "https://cre-api.kufar.by"
    SEARCH_PATH = "/ads-search/v1/engine/v1/search/rendered-paginated"
    CATEGORIES_PATH = "/category_tree/v1/category_tree"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search kufar ads by query and category"""

        url = f"{self.SEARCH_PATH}?query={query}"

        if options:
            if options.get("category"):
                url += f"&cat={options['category']}"
            if options.get("language"):
                url += f"&lang={options['language']}"
            size = options.get("size", 10)
            if size:
                url += f"&size={size}"

        return await self.connect(GET, self.BASE_URL, url)

    async def get_all_categories(self) -> APIResponse:
        """Get all existing categories"""
        return await self.connect(GET, self.BASE_URL, self.CATEGORIES_PATH)


class KufarSearchService(GameSearchService):
    """Service for work with Kufar api"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Search ads by game name"""
        search_response = await self._client.search(
            query, {"category": self._game_category_id}
        )
        products = self.filter_results(search_response.response["ads"])
        return self.build_results(products)
