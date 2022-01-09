"""
Wildberries API Client
"""
from typing import Optional, Tuple

from bgd.constants import WILDBERRIES
from bgd.responses import GameSearchResult, Price
from bgd.services.abc import GameSearchResultFactory
from bgd.services.api_clients import JsonHttpApiClient
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.responses import APIResponse


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


class WildberriesSearchService(GameSearchService):
    """Service for work with Wildberries api"""

    async def do_search(self, query: str, *args, **kwargs) -> Tuple[GameSearchResult]:
        search_results = await self._client.search(query)
        products = self.filter_results(
            search_results.response["data"]["products"], self._is_available_game
        )
        return self.build_results(products)

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        return product.get("subjectId") == self._game_category_id

    @property
    def result_factory(self) -> GameSearchResultFactory:
        """Creates result factory"""
        return WildberriesGameSearchResultFactory()


class WildberriesGameSearchResultFactory:
    """Build GameSearchResult for Wildberrries datasource"""

    ITEM_URL = "https://by.wildberries.ru/catalog/{}/detail.aspx"
    IMAGE_URL = "https://images.wbstatic.net/big/new/{}0000/{}-1.jpg"

    def create(self, search_result: dict) -> GameSearchResult:
        """Creates game search result"""
        return GameSearchResult(
            description="",
            images=self._extract_images(search_result),
            location=None,
            owner=None,
            prices=[self._extract_price(search_result)],
            source=WILDBERRIES,
            subject=self._extract_subject(search_result),
            url=self._extract_url(search_result),
        )

    @staticmethod
    def _extract_price(product: dict) -> Price:
        """Extract prices for product in different currencies"""
        price_in_byn: int = product["salePriceU"]
        return Price(amount=price_in_byn)

    def _extract_url(self, product: dict) -> str:
        """Extract url to product"""
        return self.ITEM_URL.format(product.get("id"))

    def _extract_images(self, product: dict) -> list:
        """Extract product images"""
        product_id = str(product.get("id"))
        return [self.IMAGE_URL.format(product_id[:4], product_id)]

    @staticmethod
    def _extract_subject(product: dict) -> str:
        """Extract product subject"""
        return f"{product.get('brand')} / {product.get('name')}"
