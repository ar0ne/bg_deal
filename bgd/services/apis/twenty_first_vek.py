"""
21.vek API Client
"""
from typing import Optional, Tuple

from bgd.constants import TWENTYFIRSTVEK
from bgd.responses import GameSearchResult, Price
from bgd.services.api_clients import JsonHttpApiClient
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.responses import APIResponse


class TwentyFirstVekApiClient(JsonHttpApiClient):
    """Api client for 21vek.by"""

    BASE_SEARCH_URL = "https://search.21vek.by/api/v1.0"
    SEARCH_PATH = "/search/suggest"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search by query string"""
        url = f"{self.SEARCH_PATH}?q={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class TwentyFirstVekSearchService(GameSearchService):
    """Search service for 21vek.by"""

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        return (
            product["type"] == "product"
            and product["price"] != "нет на складе"
            and "board_games" in product["url"]
        )

    async def do_search(self, query: str, *args, **kwargs) -> Tuple[GameSearchResult]:
        """Search on api and build response"""
        response = await self._client.search(query, **kwargs)
        products = self.filter_results(response.response["items"], self._is_available_game)
        return self.build_results(products)


class TwentyFirstVekGameSearchResultFactory:
    """Factory for search results from 21vek"""

    BASE_URL = "https://21vek.by"

    def create(self, search_result: dict) -> GameSearchResult:
        """Creates search result"""
        return GameSearchResult(
            description=search_result["highlighted"],
            images=self._extract_images(search_result),
            location=None,
            owner=None,
            prices=[self._extract_price(search_result)],
            source=TWENTYFIRSTVEK,
            subject=search_result["name"],
            url=self._extract_url(search_result),
        )

    @staticmethod
    def _extract_price(product: dict) -> Price:
        """Extract price"""
        # "price": "60,00 р."
        price = product["price"]
        price = price.split(" ")[0]
        price = int(price.replace(",", ""))
        return Price(amount=price)

    def _extract_url(self, product: dict) -> str:
        """Extract product url"""
        return f"{self.BASE_URL}{product['url']}"

    @staticmethod
    def _extract_images(product: dict) -> list[str]:
        """Extract product images"""
        pic_url = product["picture"]
        bigger_img = pic_url.replace("preview_s", "preview_b")
        return [bigger_img]
