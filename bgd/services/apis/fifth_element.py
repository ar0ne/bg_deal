"""
5 element API Client
"""
from typing import List, Optional

from bgd.responses import GameSearchResult
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
        game_category_id: str,
        result_builder: GameSearchResultBuilder,
        search_app_id: str,
        currency_exchange_rate_converter: CurrencyExchangeRateService,
    ) -> None:
        """Init 5th element Search Service"""
        # there are more than one category that we should check
        self._game_category_ids = game_category_id.split(",")
        super().__init__(
            client, game_category_id, result_builder, currency_exchange_rate_converter
        )
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
