"""
Wildberries API Client
"""
from typing import Optional

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import JsonHttpApiClient
from bgd.api_clients.responses import APIResponse


class WildberriesApiClient(JsonHttpApiClient):
    """Client for Wildberries API"""

    BASE_SEARCH_URL = "https://wbxsearch-by.wildberries.ru"
    BASE_CATALOG_URL = "https://wbxcatalog-sng.wildberries.ru"
    SEARCH_PATH = "/exactmatch/common"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search items by query"""
        url = await self._build_search_query_url(query)
        return await self.connect(GET, self.BASE_CATALOG_URL, url)

    async def _build_search_query_url(
        self,
        query: str,
        locale: str = "by",
        language: Optional[str] = "ru",
        currency: Optional[str] = "byn",
    ) -> str:
        """
        Build query url for searching income text.
        e.g. /presets/bucket_71/catalog?locale=by&lang=ru&curr=rub&brand=32823
        """
        # firstly, we need to get shard info and query
        shard_response = await self._get_shard_and_query(query)
        shard_key = shard_response.response.get("shardKey")
        query_key_value = shard_response.response.get("query")

        url = f"/{shard_key}/catalog?{query_key_value}&locale={locale}"

        if language:
            url += f"&lang={language}"
        if currency:
            url += f"&curr={currency}"

        return url

    async def _get_shard_and_query(self, query: str):
        """
        Firstly, we need to get right shard and query key-value, e.g.
        {
          "name": "monopoly",
          "query": "preset=10134421",
          "shardKey": "presets/bucket_71",
          "filters": "xsubject;dlvr;brand;price;kind;color;wbsize;season;consists"
        }

        """
        url = f"{self.SEARCH_PATH}?query={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)
