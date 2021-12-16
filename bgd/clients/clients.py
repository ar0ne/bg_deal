"""
Api clients
"""
import json
import logging
from typing import Optional, Protocol, Union

import aiohttp
from aiohttp import ClientResponse
from libbgg.infodict import InfoDict

from bgd.clients.responses import (
    APIRequest,
    APIResponse,
    JSONAPIResponse,
    XMLAPIResponse,
)
from bgd.errors import ApiClientError, PageNotFoundError

log = logging.getLogger(__name__)

GET = "GET"


def handle_response(response: ClientResponse) -> None:
    """Handle response status and raise exception if needed"""
    status = response.status
    if status == 404:
        log.warning("PageNotFound error occurs for response %s", response)
        raise PageNotFoundError(str(response.url))
    if not 200 <= status < 300:
        log.warning("ApiClient error occurs for response %s", response)
        raise ApiClientError(str(status))


class IApiClient(Protocol):
    """api client interface"""

    async def connect(
        self,
        method: str,
        base_url: str,
        path: str,
        body: Optional[str] = None,
        headers: Optional[dict] = None,
    ) -> APIResponse:
        ...

    @staticmethod
    def prepare_request(**kwargs) -> APIRequest:
        ...

    @staticmethod
    async def prepare_response(response: ClientResponse) -> APIResponse:
        ...


class Connector:
    """Simple API connector"""

    async def connect(
        self,
        method: str,
        base_url: str,
        path: str,
        body: Optional[str] = None,
        headers: Optional[dict] = None,
    ) -> APIResponse:
        """Connect Api to resource"""
        async with aiohttp.ClientSession() as session:
            url = base_url + path
            request = self.prepare_request(
                method=method, url=url, headers=headers, body=body
            )
            async with session.request(**request.to_dict()) as resp:
                handle_response(resp)
                return await self.prepare_response(resp)


class JSONResource:
    """Json Resource"""

    @staticmethod
    def prepare_request(**kwargs: dict) -> APIRequest:
        """Prepare request to work with JSON resources"""
        body = kwargs.pop("body", None)
        body = None if not body else json.dumps(body)
        return APIRequest(**kwargs, json=body)

    @staticmethod
    async def prepare_response(response: ClientResponse) -> JSONAPIResponse:
        """Prepare response from Json resource"""
        r_json = await response.json(content_type=None)
        return JSONAPIResponse(r_json, response.status)


class XMLResource:
    """XML Resource"""

    @staticmethod
    def prepare_request(**kwargs) -> APIRequest:
        """Prepare request to work with XML resource"""
        return APIRequest(**kwargs)

    @staticmethod
    async def prepare_response(response: ClientResponse) -> XMLAPIResponse:
        """Prepare response from XML resource"""
        r_text = await response.text(encoding=None)
        info_dict = InfoDict.xml_to_info_dict(r_text, strip_errors=True)
        return XMLAPIResponse(info_dict, response.status)


class JSONAPIClient(JSONResource, Connector):
    """Json API client"""


class XMLAPIClient(XMLResource, Connector):
    """Xml API client"""


class GameSearcher(Protocol):
    """Api client for searching games"""

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search by query"""
        ...


class GameInfoSearcher(Protocol):
    """Api client for game info searching"""

    async def search_game_info(
        self, query: str, options: Optional[dict] = None
    ) -> APIResponse:
        """Search info about game"""
        ...

    async def get_game_details(self, game_alias: Union[str, int]) -> APIResponse:
        """Get info about the game"""
        ...


class KufarApiClient(GameSearcher, JSONAPIClient):
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


class WildberriesApiClient(GameSearcher, JSONAPIClient):
    """Client for Wildberries API"""

    BASE_SEARCH_URL = "https://wbxsearch-by.wildberries.ru"
    BASE_CATALOG_URL = "https://wbxcatalog-sng.wildberries.ru"
    SEARCH_PATH = "/exactmatch/common"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
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
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class OzonApiClient(GameSearcher, JSONAPIClient):
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


class OzByApiClient(GameSearcher, JSONAPIClient):
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


class OnlinerApiClient(GameSearcher, JSONAPIClient):
    """Api client for onliner.by"""

    BASE_SEARCH_URL = "https://catalog.onliner.by/sdapi"
    SEARCH_PATH = "/catalog.api/search/products"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search by query string"""
        url = f"{self.SEARCH_PATH}?query={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class TwentyFirstVekApiClient(GameSearcher, JSONAPIClient):
    """Api client for 21vek.by"""

    BASE_SEARCH_URL = "https://search.21vek.by/api/v1.0"
    SEARCH_PATH = "/search/suggest"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search by query string"""
        url = f"{self.SEARCH_PATH}?q={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class FifthElementApiClient(GameSearcher, JSONAPIClient):
    """Api client for 5element.by"""

    BASE_SEARCH_URL = "https://api.multisearch.io"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search query string"""
        search_app_id = options["search_app_id"]  # type: ignore
        url = f"?query={query}&id={search_app_id}&lang=ru&autocomplete=true"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class VkontakteApiClient(GameSearcher, JSONAPIClient):
    """Api client for vk.com"""

    BASE_URL = "https://api.vk.com/method"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search query on group wall"""
        options = options or {}
        group_id = f"-{options['group_id']}"
        url = (
            f"/wall.get"
            f"?owner_id={group_id}"
            f"&v={options['api_version']}"
            f"&count={options['limit']}"
            f"&access_token={options['api_token']}"
        )
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        return await self.connect(GET, self.BASE_URL, url, headers=headers)


class BoardGameGeekApiClient(GameInfoSearcher, XMLAPIClient):
    """Api client for BoardGameGeek"""

    BASE_URL = "https://api.geekdo.com/xmlapi2"
    SEARCH_PATH = "/search"
    THING_PATH = "/thing"

    async def search_game_info(
        self,
        query: str,
        options: Optional[dict] = None,
    ) -> APIResponse:
        """Search game by exact(1) query in game_type(boardgame) section"""
        options = options or {}
        game_type = options.get("game_type", "boardgame")
        exact = options.get("exact", True)
        url = f"{self.SEARCH_PATH}?exact={1 if exact else 0}&type={game_type}&query={query}"
        return await self.connect(GET, self.BASE_URL, url)

    async def get_game_details(self, game_alias: Union[str, int]) -> APIResponse:
        """Get details about the game by id"""
        url = f"{self.THING_PATH}?stats=1&id={game_alias}"
        return await self.connect(GET, self.BASE_URL, url)


class TeseraApiClient(GameInfoSearcher, JSONAPIClient):
    """Api client for tesera.ru"""

    BASE_URL = "https://api.tesera.ru"
    SEARCH_PATH = "/search/games"
    GAMES_PATH = "/games"

    async def search_game_info(
        self, query: str, options: Optional[dict] = None
    ) -> APIResponse:
        """Search game info"""
        url = f"{self.SEARCH_PATH}?query={query}"
        return await self.connect(GET, self.BASE_URL, url)

    async def get_game_details(self, game_alias: Union[str, int]) -> APIResponse:
        """Get game details by alias"""
        url = f"{self.GAMES_PATH}/{game_alias}"
        return await self.connect(GET, self.BASE_URL, url)
