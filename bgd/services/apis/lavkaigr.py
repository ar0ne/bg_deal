"""
API Client for lavkaigr.ru
"""


from typing import List, Optional

from bs4 import BeautifulSoup

from bgd.constants import LAVKAIGR, RUB
from bgd.responses import GameSearchResult, Price
from bgd.services.abc import GameSearchResultFactory
from bgd.services.api_clients import HtmlHttpApiClient
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.responses import APIResponse
from bgd.services.utils import text_contains


class LavkaIgrApiClient(HtmlHttpApiClient):
    """API client for lavkaigr.ru"""

    BASE_SEARCH_URL = "https://www.lavkaigr.ru/shop/search/"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search query string"""
        query = "+".join(query.split(" "))
        url = f"?query={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class LavkaIgrSearchService(GameSearchService):
    """Search service for lavkaigr.ru"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Search query"""
        html_page = await self._client.search(query)
        # find products on search page
        soup = BeautifulSoup(html_page.response, "html.parser")

        search_results = soup.find(class_="product-list")
        items = search_results.find_all(class_="block")
        products = []
        for item in items:
            # filter unavailable products
            if not item.find(class_="bottom").find(class_="buy-mini"):
                continue
            name = item.find(class_="game-name").get_text().strip()
            # filter not relevant products
            if not text_contains(name, query):
                continue
            product = {
                "image": item.find(class_="photo").find("img")["src"],
                "name": name,
                "price": item.find(class_="price").get_text().strip(),
                "url": item.find(class_="game-name")["href"],
            }
            products.append(product)

        return self.build_results(products)

    @property
    def result_factory(self) -> GameSearchResultFactory:
        """Creates result factory"""
        return LavkaIgrGameSearchResultFactory()


class LavkaIgrGameSearchResultFactory:
    """Game search result factory for lavka igr"""

    BASE_URL = "https://lavkaigr.ru"

    def create(self, search_result: dict) -> GameSearchResult:
        """Creates game search result"""
        return GameSearchResult(
            description="",
            images=self._extract_images(search_result),
            location=None,
            owner=None,
            prices=[self._extract_price(search_result)],
            source=LAVKAIGR,
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
        Cut the price ending, e.g. `1232 pуб.` -> 1232
        """
        raw_price = product["price"][:-4]
        raw_price = raw_price.replace(" ", "")
        amount = int(float(raw_price) * 100)
        return Price(amount=amount, currency=RUB)

    def _extract_url(self, product: dict) -> str:
        """Extract product url"""
        return f"{self.BASE_URL}{product['url']}"
