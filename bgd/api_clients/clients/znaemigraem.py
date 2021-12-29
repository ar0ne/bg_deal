"""
Api Client for znaemigraem.by
"""
from typing import Optional

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import HtmlHttpApiClient
from bgd.api_clients.responses import APIResponse


class ZnaemIgraemApiClient(HtmlHttpApiClient):
    """Api client for 5element.by"""

    BASE_SEARCH_URL = "https://znaemigraem.by"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search query string"""
        query = "+".join(query.split(" "))
        url = f"/catalog/?q={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)
