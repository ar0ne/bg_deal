"""
Api clients
"""
import json
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

import aiohttp


@dataclass
class APIResponse:
    response: dict
    status: int


class ApiClient:
    """Abstract api client"""

    async def connect(
        self,
        method: str,
        base_url: str,
        path: str,
        request_body_dict: str = "",
        headers: Optional[dict] = None,
    ) -> APIResponse:
        async with aiohttp.ClientSession() as session:
            url = base_url + path
            headers = headers or {}
            body_json = json.dumps(request_body_dict)
            async with session.request(
                method, url, headers=headers, json=body_json
            ) as resp:
                response = await resp.json(content_type=None)
                if not 200 <= resp.status < 300:
                    # todo: raise error
                    return APIResponse({"error": "something went wrong"}, 500)
                return APIResponse(response, 200)

    @abstractmethod
    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search by query"""


class KufarApiClient(ApiClient):
    """Client for Kufar API"""

    BASE_URL = "https://cre-api.kufar.by"
    SEARCH_PATH = "/ads-search/v1/engine/v1/search/rendered-paginated"
    CATEGORIES_PATH = "/category_tree/v1/category_tree"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search kufar ads by query and category"""

        url = f"{self.SEARCH_PATH}?query={query}"

        if options.get("category"):
            url += f"&cat={options['category']}"
        if options.get("language"):
            url += f"&lang={options['language']}"

        return await self.connect("GET", self.BASE_URL, url)

    async def get_all_categories(self) -> APIResponse:
        """Get all existing categories"""
        return await self.connect("GET", self.BASE_URL, self.CATEGORIES_PATH)


class WildberriesApiClient(ApiClient):
    """Client for Wildberries API"""

    BASE_SEARCH_URL = "https://wbxsearch-by.wildberries.ru"
    BASE_CATALOG_URL = "https://wbxcatalog-sng.wildberries.ru"
    SEARCH_PATH = "/exactmatch/common"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search items by query"""

        # firstly we need to get shard info and query
        query_response = await self._get_query(query)
        shard_key = query_response.response.get("shardKey")
        query_key_value = query_response.response.get("query")

        return await self._get_catalog_items(shard_key, query_key_value)

    async def _get_query(self, query: str):
        """

        {
          "name": "monopoly",
          "query": "preset=10134421",
          "shardKey": "presets/bucket_71",
          "filters": "xsubject;dlvr;brand;price;kind;color;wbsize;season;consists"
        }

        """
        url = f"{self.SEARCH_PATH}?query={query}"
        return await self.connect("GET", self.BASE_SEARCH_URL, url)

    async def _get_catalog_items(
        self,
        shard_key: str,
        query: str,
        locale: str = "by",
        language: Optional[str] = "ru",
        currency: Optional[str] = "byn",
    ) -> APIResponse:
        # /presets/bucket_71/catalog?locale=by&lang=ru&curr=rub&brand=32823
        url = f"/{shard_key}/catalog?{query}&locale={locale}"

        if language:
            url += f"&lang={language}"
        if currency:
            url += f"&curr={currency}"

        return await self.connect("GET", self.BASE_CATALOG_URL, url)
