"""
VKontakte (vk.com) API Client
"""
import re
from typing import List, Optional

from bgd.responses import GameSearchResult
from bgd.services.base import CurrencyExchangeRateService, GameSearchService
from bgd.services.builders import GameSearchResultBuilder
from bgd.services.constants import GET
from bgd.services.protocols import GameSearcher, JsonHttpApiClient
from bgd.services.responses import APIResponse


class VkontakteApiClient(JsonHttpApiClient):
    """Api client for vk.com"""

    BASE_URL = "https://api.vk.com/method"

    async def search(self, _: str, options: Optional[dict] = None) -> APIResponse:
        """Search query on group wall"""
        options = options or {}
        group_id = f"-{options['group_id']}"
        url = (
            f"/wall.get"
            f"?owner_id={group_id}"
            f"&v={options['api_version']}"
            f"&count={options['limit']}"
            f"&access_token={options['api_token']}"
        )
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        return await self.connect(GET, self.BASE_URL, url, headers=headers)


class VkontakteSearchService(GameSearchService):
    """Search service for vk.com"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        client: GameSearcher,
        game_category_id: str,
        result_builder: GameSearchResultBuilder,
        api_version: str,
        api_token: str,
        group_id: str,
        group_name: str,
        limit: int,
        currency_exchange_rate_converter: CurrencyExchangeRateService,
    ) -> None:
        """Init 5th element Search Service"""
        # there are more than one category that we should check
        super().__init__(
            client, game_category_id, result_builder, currency_exchange_rate_converter
        )
        self.api_version = api_version
        self.api_token = api_token
        self.group_id = group_id
        self.group_name = group_name
        self.limit = limit
        self._query = ""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        self._query = query
        search_response = await self._client.search(
            query,
            {
                "api_token": self.api_token,
                "api_version": self.api_version,
                "group_id": self.group_id,
                "limit": self.limit,
            },
        )
        products = self.filter_results(
            search_response.response["response"]["items"], self._is_available_game
        )
        return self.build_results(products)

    def _is_available_game(self, product: dict) -> bool:
        """True if it's available board game"""
        # @todo: is it possible to do it better?  # typing: disable=fixme
        if not self._query:
            return False
        return re.search(self._query, product["text"], re.IGNORECASE)  # type: ignore
