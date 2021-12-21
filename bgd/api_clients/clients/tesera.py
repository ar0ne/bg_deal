"""
Tesera.ru API Client
"""
from typing import Optional, Union

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import JsonHttpApiClient
from bgd.api_clients.responses import APIResponse


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
