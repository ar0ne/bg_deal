"""
Onliner (catalog) API Client
"""
from typing import Optional

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import JsonHttpApiClient
from bgd.api_clients.responses import APIResponse


class OnlinerApiClient(JsonHttpApiClient):
    """Api client for onliner.by"""

    BASE_SEARCH_URL = "https://catalog.onliner.by/sdapi"
    SEARCH_PATH = "/catalog.api/search/products"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search by query string"""
        url = f"{self.SEARCH_PATH}?query={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)
