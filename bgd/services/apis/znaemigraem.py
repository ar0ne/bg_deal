"""
Api Client for znaemigraem.by
"""
from typing import List, Optional

from bs4 import BeautifulSoup

from bgd.responses import GameSearchResult
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.protocols import HtmlHttpApiClient
from bgd.services.responses import APIResponse


class ZnaemIgraemApiClient(HtmlHttpApiClient):
    """Api client for 5element.by"""

    BASE_SEARCH_URL = "https://znaemigraem.by"

    async def search(self, query: str, _: Optional[dict] = None) -> APIResponse:
        """Search query string"""
        query = "+".join(query.split(" "))
        url = f"/catalog/?q={query}"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class ZnaemIgraemSearchService(GameSearchService):
    """Search service for znaemigraem.by"""

    def _is_available_game(self, product: dict) -> bool:
        """True if game is available for purchase"""
        return product["available"]

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Search query"""
        html_page = await self._client.search(query)
        # find products on search page
        soup = BeautifulSoup(html_page.response, "html.parser")

        search_results = soup.find(class_="c-search__results")
        items = search_results.find_all(class_="catalog-item")
        products = []
        for item in items:
            # filter unavailable products
            if item.find(class_="catalog-item__amount").find("span"):
                continue
            product = {
                "image": item.find("img")["src"],
                "name": item.find(class_="name").get_text(),
                "price": item.find(class_="catalog-item__price").get_text(),
                "url": item.find(class_="image")["href"],
            }
            products.append(product)

        return self.build_results(products)
