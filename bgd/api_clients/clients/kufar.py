"""
Kufar.by API Client
"""
from typing import Optional

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import JsonHttpApiClient
from bgd.api_clients.responses import APIResponse


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
