"""
Ozon.ru API Client
"""
from typing import Optional

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import JsonHttpApiClient
from bgd.api_clients.responses import APIResponse


class OzonApiClient(JsonHttpApiClient):
    """Api client for ozon.ru"""

    BASE_SEARCH_URL = "https://www.ozon.ru"
    SEARCH_PATH = "/api/composer-api.bx/page/json/v2?url=/category"
    HEADERS = {
        "dnt": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/89.0.4389.82 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
        "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "purpose": "prefetch",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,ru;q=0.8",
    }

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search items by query"""
        category = options["category"]  # type: ignore
        url = f"{self.SEARCH_PATH}/{category}?text={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url, headers=self.HEADERS)
