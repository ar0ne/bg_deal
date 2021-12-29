"""
5 element API Client
"""
from typing import List, Optional

from bgd.constants import FIFTHELEMENT
from bgd.responses import GameSearchResult, Price
from bgd.services.base import CurrencyExchangeRateService, GameSearchService
from bgd.services.builders import GameSearchResultBuilder
from bgd.services.constants import GET
from bgd.services.protocols import GameSearcher, JsonHttpApiClient
from bgd.services.responses import APIResponse


class FifthElementApiClient(JsonHttpApiClient):
    """Api client for 5element.by"""

    BASE_SEARCH_URL = "https://api.multisearch.io"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search query string"""
        search_app_id = options["search_app_id"]  # type: ignore
        url = f"?query={query}&id={search_app_id}&lang=ru&autocomplete=true"
        return await self.connect(GET, self.BASE_SEARCH_URL, url)


class FifthElementSearchService(GameSearchService):
    """Search service for 5element.by"""

    def __init__(
        self,
        client: GameSearcher,
        result_builder: GameSearchResultBuilder,
        currency_exchange_rate_converter: CurrencyExchangeRateService,
        game_category_id: str,
        search_app_id: str,
    ) -> None:
        """Init 5th element Search Service"""
        # there are more than one category that we should check
        self._game_category_ids = game_category_id.split(",")
        super().__init__(client, result_builder, currency_exchange_rate_converter)
        self._search_app_id = search_app_id

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        response = await self._client.search(
            query, {"search_app_id": self._search_app_id}
        )
        products = self.filter_results(
            response.response["results"]["items"], self._is_available_game
        )
        return self.build_results(products)

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        return (
            product["is_presence"]
            and product["params_data"]["category_id"] in self._game_category_ids
        )


class GameSearchResultFifthElementBuilder(GameSearchResultBuilder):
    """Builder for GameSearch results from 5element"""

    BASE_URL = "https://5element.by"

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Build search result"""
        return GameSearchResult(
            description="",
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=FIFTHELEMENT,
            subject=search_result["name"],
            url=cls._extract_url(search_result),
        )

    @staticmethod
    def _extract_images(product: dict) -> list[str]:
        """Extract product images"""
        return [product["picture"]]

    @staticmethod
    def _extract_price(product: dict) -> Optional[Price]:
        """Extract price"""
        price = product["price"] * 100
        return Price(amount=price)

    @classmethod
    def _extract_url(cls, product: dict) -> str:
        """Extract product url"""
        return f"{cls.BASE_URL}{product['url']}"