"""
VKontakte (vk.com) API Client
"""
import itertools
import re
from typing import Optional, Tuple

from bgd.constants import VK
from bgd.responses import GameOwner, GameSearchResult
from bgd.services.abc import GameSearchResultFactory
from bgd.services.api_clients import GameSearcher, JsonHttpApiClient
from bgd.services.base import CurrencyExchangeRateService, GameSearchService
from bgd.services.constants import GET
from bgd.services.responses import APIResponse
from bgd.services.utils import remove_backslashes


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
        currency_exchange_rate_converter: CurrencyExchangeRateService,
        api_version: str,
        api_token: str,
        group_id: str,
        group_name: str,
        limit: int,
        game_category_id: str = "",
    ) -> None:
        """Init 5th element Search Service"""
        # there are more than one category that we should check
        super().__init__(client, currency_exchange_rate_converter, game_category_id)
        self.api_version = api_version
        self.api_token = api_token
        self.group_id = group_id
        self.group_name = group_name
        self.limit = limit
        self._query = ""

    async def do_search(self, query: str, *args, **kwargs) -> Tuple[GameSearchResult]:
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

    @property
    def result_factory(self) -> GameSearchResultFactory:
        """Creates result factory"""
        return VKontakteGameSearchResultFactory()


class VKontakteGameSearchResultFactory:
    """Factory for search results from vk.com"""

    BASE_URL = "https://vk.com"
    GROUP_POST_PATH = "/{}?w=wall{}_{}"

    def create(self, search_result: dict) -> GameSearchResult:
        """Create game search result"""
        return GameSearchResult(
            description=search_result["text"],
            images=self._extract_images(search_result),
            location=None,
            owner=self._extract_owner(search_result),
            prices=None,
            source=VK,
            subject="VK post",
            url=self._extract_url(search_result),
        )

    def _extract_url(self, post: dict) -> str:
        """Extract wall post url"""
        # todo: group name should come from configs  # pylint: disable=fixme
        return self.BASE_URL + self.GROUP_POST_PATH.format(
            "baraholkanastolokrb", post["owner_id"], post["id"]
        )

    @classmethod
    def _extract_images(cls, post: dict) -> list:
        """Extract images"""
        photo_attachments = filter(lambda it: it["type"] == "photo", post["attachments"])
        all_photos = map(lambda a: a["photo"]["sizes"], photo_attachments)
        photos = itertools.chain.from_iterable(all_photos)
        highest_resolution_photos = filter(lambda s: s["type"] == "z", photos)
        return list(map(lambda ph: remove_backslashes(ph["url"]), highest_resolution_photos))

    def _extract_owner(self, post: dict) -> GameOwner:
        """extract post owner"""
        user_id = post["signer_id"]
        return GameOwner(
            id=user_id,
            name="",
            url=f"{self.BASE_URL}/id{user_id}",
        )
