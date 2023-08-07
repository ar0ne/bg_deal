"""
API Client for crowdgames.ru
"""


from typing import Optional, Tuple

from bs4 import BeautifulSoup

from bgd.constants import CROWDGAMES, RUB
from bgd.responses import GameSearchResult, Price
from bgd.services.api_clients import HtmlHttpApiClient
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.responses import APIResponse
from bgd.services.utils import text_contains


class CrowdGamesApiClient(HtmlHttpApiClient):
    """API client for crowdgames.ru"""

    BASE_SEARCH_URL = "https://www.crowdgames.ru/search/"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search query string"""
        query = "+".join(query.split(" "))
        url = f"?q={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class CrowdGamesSearchService(GameSearchService):
    """Search service for crowdgames.ru"""

    async def do_search(self, query: str, *args, **kwargs) -> Tuple[GameSearchResult]:
        """Search query"""
        html_page = await self._client.search(query)
        # find products on search page
        soup = BeautifulSoup(html_page.response, "html.parser")

        items = soup.find_all(class_="div-prod")
        products = []
        for item in items:
            # filter unavailable products
            if not self._product_available(item):
                continue
            name = item.find(class_="titile-prod").get_text().strip()
            # filter not relevant products
            if not text_contains(name, query):
                continue
            product = {
                "image": item.find(class_="div-img-prod").find("img")["src"],
                "name": name,
                "price": item.find(class_="price-prod").get_text().strip(),
                "url": item.find(class_="a-prod").select_one("a")["href"],
            }
            products.append(product)

        return self.build_results(products)

    def _product_available(self, item) -> bool:
        """True if product available for purchase"""
        return bool(item.find(class_="ostatok-prod").select_one("a").get_text().strip())


class CrowdGamesGameSearchResultFactory:
    """Game search result factory for crowdgames"""

    BASE_URL = "https://www.crowdgames.ru"

    def create(self, search_result: dict) -> GameSearchResult:
        """Creates game search result"""
        return GameSearchResult(
            description="",
            images=self._extract_images(search_result),
            location=None,
            owner=None,
            prices=[self._extract_price(search_result)],
            source=CROWDGAMES,
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
