"""
5 element API Client
"""
from typing import Optional

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import JsonHttpApiClient
from bgd.api_clients.responses import APIResponse


class FifthElementApiClient(JsonHttpApiClient):
    """Api client for 5element.by"""

    BASE_SEARCH_URL = "https://api.multisearch.io"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search query string"""
        search_app_id = options["search_app_id"]  # type: ignore
        url = f"?query={query}&id={search_app_id}&lang=ru&autocomplete=true"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)
