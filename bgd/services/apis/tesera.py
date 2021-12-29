"""
Tesera.ru API Client
"""
from typing import Optional, Union

from bgd.services.base import GameInfoService
from bgd.services.constants import GET
from bgd.services.protocols import JsonHttpApiClient
from bgd.services.responses import APIResponse
from bgd.services.types import GameAlias, JsonResponse


class TeseraApiClient(JsonHttpApiClient):
    """Api client for tesera.ru"""

    BASE_URL = "https://api.tesera.ru"
    SEARCH_PATH = "/search/games"
    GAMES_PATH = "/games"

    async def search_game_info(
        self, query: str, _: Optional[dict] = None
    ) -> APIResponse:
        """Search game info"""
        url = f"{self.SEARCH_PATH}?query={query}"
        return await self.connect(GET, self.BASE_URL, url)

    async def get_game_details(self, game_alias: Union[str, int]) -> APIResponse:
        """Get game details by alias"""
        url = f"{self.GAMES_PATH}/{game_alias}"
        return await self.connect(GET, self.BASE_URL, url)


class TeseraGameInfoService(GameInfoService):
    """Game info service for tesera.ru"""

    def get_game_alias(self, search_results: JsonResponse) -> Optional[GameAlias]:
        """Choose the game from search response and returns alias"""
        # take first item in the list
        if len(search_results) and isinstance(search_results, list):
            return search_results[0]["alias"]
        return None
