"""
Oz.by API Client
"""
from typing import List, Optional

from bgd.constants import OZBY
from bgd.responses import GameSearchResult, Price
from bgd.services.abc import GameSearchResultBuilder
from bgd.services.api_clients import JsonHttpApiClient
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.responses import APIResponse


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


class OzBySearchService(GameSearchService):
    """Search service for oz.by"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(query, {"category": self._game_category_id, **kwargs})
        products = self.filter_results(response.response["data"])
        return self.build_results(products)


class GameSearchResultOzByBuilder(GameSearchResultBuilder):
    """GameSearchResult Builder for oz.by"""

    GAME_URL = "https://oz.by/boardgames/more{}.html"

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Builds game search result from ozon data source search result"""
        return GameSearchResult(
            description=cls._extract_description(search_result),
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=OZBY,
            subject=cls._extract_subject(search_result),
            url=cls._extract_url(search_result),
        )

    @staticmethod
    def _extract_images(item: dict) -> list[str]:
        """Get image of the game"""
        return [item["attributes"]["main_image"]["200"]]

    @staticmethod
    def _extract_price(item: dict) -> Optional[Price]:
        """Extract game prices"""
        price = item["attributes"]["cost"]["decimal"]
        if not price:
            return None
        return Price(amount=price * 100)

    @staticmethod
    def _extract_subject(item: dict) -> str:
        """Extracts subject"""
        return item["attributes"]["title"]

    @classmethod
    def _extract_url(cls, item: dict) -> str:
        """Extracts item url"""
        return cls.GAME_URL.format(item["id"])

    @staticmethod
    def _extract_description(item: dict) -> str:
        """Extract item description"""
        return item["attributes"].get("small_desc")
