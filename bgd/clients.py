"""
Api clients
"""
import json
import logging
from abc import abstractmethod
from typing import Optional

import aiohttp
from aiohttp import ClientResponse
from starlette.datastructures import Headers

from bgd.errors import ApiClientError, NotFoundApiClientError
from bgd.responses import APIResponse

log = logging.getLogger(__name__)


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
            body_json = json.dumps(request_body_dict)
            async with session.request(
                method, url, headers=headers, json=body_json
            ) as resp:
                self._handle_response(resp)
                r_json = await resp.json(content_type=None)
                return APIResponse(r_json, 200)

    @staticmethod
    def _handle_response(response: ClientResponse) -> None:
        """Handle response status and raise exception if needed"""
        status = response.status
        if status == 404:
            log.warning("NotFoundApiClient error occurs for response %s", response)
            raise NotFoundApiClientError(str(response.url))
        if not 200 <= status < 300:
            log.warning("ApiClient error occurs for response %s", response)
            raise ApiClientError(str(status))

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
        size = options.get("size", 10)
        if size:
            url += f"&size={size}"

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
        url = await self._build_search_query_url(query)
        return await self.connect("GET", self.BASE_CATALOG_URL, url)

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
        # firstly we need to get shard info and query
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
        return await self.connect("GET", self.BASE_SEARCH_URL, url)


class OzonApiClient(ApiClient):
    """Api client for ozon.ru"""

    BASE_SEARCH_URL = "https://www.ozon.ru"
    SEARCH_PATH = "/api/composer-api.bx/page/json/v2?url=/category/{}/?text="

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search items by query"""
        url = self.SEARCH_PATH.format(options.get("category")) + query
        return await self.connect(
            "GET", self.BASE_SEARCH_URL, url, headers=self._headers
        )

    @property
    def _headers(self) -> dict:
        """Prepare income headers for sending to ozon api"""
        return {
            "connection": "keep-alive",
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "purpose": "prefetch",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,ru;q=0.8",
        }
