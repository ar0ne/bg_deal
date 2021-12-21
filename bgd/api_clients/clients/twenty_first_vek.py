"""
21.vek API Client
"""
from typing import Optional

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import JsonHttpApiClient
from bgd.api_clients.responses import APIResponse


class TwentyFirstVekApiClient(JsonHttpApiClient):
    """Api client for 21vek.by"""

    BASE_SEARCH_URL = "https://search.21vek.by/api/v1.0"
    SEARCH_PATH = "/search/suggest"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search by query string"""
        url = f"{self.SEARCH_PATH}?q={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)
