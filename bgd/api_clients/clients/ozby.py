"""
Oz.by API Client
"""
from typing import Optional

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import JsonHttpApiClient
from bgd.api_clients.responses import APIResponse


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
