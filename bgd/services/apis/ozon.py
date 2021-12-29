"""
Ozon.ru API Client
"""
import html
import json
from typing import List, Optional

from bgd.constants import OZON
from bgd.responses import GameSearchResult, Price
from bgd.services.base import GameSearchService
from bgd.services.builders import GameSearchResultBuilder
from bgd.services.constants import GET
from bgd.services.protocols import JsonHttpApiClient
from bgd.services.responses import APIResponse


class OzonApiClient(JsonHttpApiClient):
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


class OzonSearchService(GameSearchService):
    """Search Service for ozon api"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(
            query, {"category": self._game_category_id, **kwargs}
        )
        results = self._extract_search_results(response.response)
        if not results:
            return []
        products = self.filter_results(results["items"])
        return self.build_results(products)

    def _extract_search_results(self, resp: dict) -> Optional[dict]:
        """Extract search results from response"""
        widget_states: dict = resp["widgetStates"]
        key = self._find_search_v2_key(widget_states)
        if not key:
            return None
        return json.loads(widget_states[key])

    @staticmethod
    def _find_search_v2_key(states: dict) -> Optional[str]:
        """Find a key in widget states"""
        for key in states.keys():
            if "searchResultsV2" in key:
                return key
        return None


class GameSearchResultOzonBuilder(GameSearchResultBuilder):
    """Builder for game search results from Ozon"""

    ITEM_URL = "https://ozon.ru"

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Builds game search result from ozon data source search result"""
        return GameSearchResult(
            description="",  # @TODO: how to get it?
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=OZON,
            subject=cls._extract_subject(search_result),
            url=cls._extract_url(search_result),
        )

    @classmethod
    def _extract_url(cls, item: dict) -> Optional[str]:
        """Extract url"""
        url = item["action"]["link"]
        if not url:
            return None
        return cls.ITEM_URL + url

    @staticmethod
    def _extract_price(item: dict) -> Optional[Price]:
        """Extract item prices in cents"""
        main_state = item.get("mainState", [])
        price_state = next(filter(lambda it: it.get("id") == "atom", main_state))
        if not price_state:
            return None
        price = price_state.get("atom").get("price").get("price")
        if not price:
            return None

        price_in_byn = int(100 * float(price.split()[0].replace(",", ".")))
        return Price(amount=price_in_byn)

    @staticmethod
    def _extract_images(item: dict) -> list:
        """Extract images"""
        return item["tileImage"]["images"] or []

    @staticmethod
    def _extract_subject(item: dict) -> str:
        """Extract item subject"""
        main_state = item.get("mainState", [])
        name_state = next(filter(lambda it: it["id"] == "name", main_state))
        if not name_state:
            return ""
        name = name_state["atom"]["textAtom"]["text"] or ""
        return html.unescape(name)
