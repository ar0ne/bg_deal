"""
BGG (board game geek) API Client
"""
from typing import Optional, Union

from libbgg.infodict import InfoDict

from ..base import GameInfoService
from ..constants import GET
from ..protocols import XmlHttpApiClient
from ..responses import APIResponse
from ..types import GameAlias


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


class BoardGameGeekGameInfoService(GameInfoService):
    """Board Game Geek service"""

    def get_game_alias(self, search_results: InfoDict) -> Optional[GameAlias]:
        """
        Get game id from result of searching.
        Skip all games without year of publishing and take the newest one.
        """
        item = search_results.get("items").get("item")
        if not item:
            return None
        if not isinstance(item, list):
            return item["id"]

        def by_published_year(game_item: dict) -> int:
            """By published year"""
            if "yearpublished" not in game_item:
                return 0
            return int(game_item["yearpublished"]["value"])

        item.sort(key=by_published_year)
        # get the newest game
        return item[-1]["id"]
