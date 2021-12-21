"""
BGG (board game geek) API Client
"""
from typing import Optional, Union

from bgd.api_clients.constants import GET
from bgd.api_clients.protocols import XmlHttpApiClient
from bgd.api_clients.responses import APIResponse


class BoardGameGeekApiClient(XmlHttpApiClient):
    """Api client for BoardGameGeek"""

    BASE_URL = "https://api.geekdo.com/xmlapi2"
    SEARCH_PATH = "/search"
    THING_PATH = "/thing"

    async def search_game_info(
        self,
        query: str,
        options: Optional[dict] = None,
    ) -> APIResponse:
        """Search game by exact(1) query in game_type(boardgame) section"""
        options = options or {}
        game_type = options.get("game_type", "boardgame")
        exact = options.get("exact", True)
        url = f"{self.SEARCH_PATH}?exact={1 if exact else 0}&type={game_type}&query={query}"
        return await self.connect(GET, self.BASE_URL, url)

    async def get_game_details(self, game_alias: Union[str, int]) -> APIResponse:
        """Get details about the game by id"""
        url = f"{self.THING_PATH}?stats=1&id={game_alias}"
        return await self.connect(GET, self.BASE_URL, url)
