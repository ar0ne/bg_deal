"""
Hobbygames.by API Client
"""
from typing import Optional, Tuple

from bs4 import BeautifulSoup

from bgd.constants import HOBBYGAMES
from bgd.responses import GameSearchResult, Price
from bgd.services.abc import GameSearchResultFactory
from bgd.services.api_clients import HtmlHttpApiClient
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.responses import APIResponse
from bgd.services.utils import text_contains


class HobbyGamesApiClient(HtmlHttpApiClient):
    """API client for hobbygames.by"""

    BASE_SEARCH_URL = "https://hobbygames.by/catalog/search"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search query string"""
        query = "+".join(query.split(" "))
        url = f"?keyword={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class HobbyGamesSearchService(GameSearchService):
    """Search service for hobby games"""

    async def do_search(self, query: str, *args, **kwargs) -> Tuple[GameSearchResult]:
        """Search query"""
        html_page = await self._client.search(query)
        # find products on search page
        soup = BeautifulSoup(html_page.response, "html.parser")

        search_results = soup.find(class_="products-container")
        if not search_results:
            return tuple()  # type: ignore
        items = search_results.find_all(class_="product-item__content")
        products = []
        for item in items:
            # filter unavailable products
            if not item.find(class_="product-cart").find(class_="price"):
                continue
            name = item.find(class_="name").get_text().strip()
            # filter not relevant products
            if not text_contains(name, query):
                continue
            product = {
                "image": item.find(class_="image").find("img")["src"],
                "name": name,
                "price": item.find(class_="price").get_text().strip(),
                "url": item.find(class_="image").find("a")["href"],
            }
            products.append(product)

        return self.build_results(products)


class HobbyGamesGameSearchResultFactory:
    """Game search result factory for hobby games"""

    def create(self, search_result: dict) -> GameSearchResult:
        """Creates game search result"""
        return GameSearchResult(
            description="",
            images=self._extract_images(search_result),
            location=None,
            owner=None,
            prices=[self._extract_price(search_result)],
            source=HOBBYGAMES,
            subject=search_result["name"],
            url=self._extract_url(search_result),
        )

    @classmethod
    def _extract_images(cls, product: dict) -> list[str]:
        """Extract product images"""
        return [product["image"]]

    @staticmethod
    def _extract_price(product: dict) -> Price:
        """
        Extract product price.
        Cut the price ending, e.g. `123.4 p.` -> 12340
        """
        amount = int(float(product["price"][:-3]) * 100)
        return Price(amount=amount)

    @classmethod
    def _extract_url(cls, product: dict) -> str:
        """Extract product url"""
        return product["url"]
