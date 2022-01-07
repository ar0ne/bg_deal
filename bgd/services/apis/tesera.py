"""
Tesera.ru API Client
"""
import html
from typing import Any, Optional, Union

from bgd.constants import NOT_AVAILABLE, TESERA
from bgd.responses import GameDetailsResult, GameStatistic
from bgd.services.abc import GameDetailsResultFactory
from bgd.services.api_clients import JsonHttpApiClient
from bgd.services.apis.bgg import BGG_GAME_URL
from bgd.services.base import GameInfoService
from bgd.services.constants import GET
from bgd.services.responses import APIResponse
from bgd.services.types import GameAlias, JsonResponse
from bgd.services.utils import clean_html


class TeseraApiClient(JsonHttpApiClient):
    """Api client for tesera.ru"""

    BASE_URL = "https://api.tesera.ru"
    SEARCH_PATH = "/search/games"
    GAMES_PATH = "/games"

    async def search_game_info(self, query: str, _: Optional[dict] = None) -> APIResponse:
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

    @property
    def result_factory(self) -> GameDetailsResultFactory:
        """Create result factory"""
        return TeseraGameDetailsResultFactory()


class TeseraGameDetailsResultFactory:
    """Factory for result for game details from Tesera service"""

    def create(self, game_info: Any) -> GameDetailsResult:
        game = game_info["game"]
        return GameDetailsResult(
            best_num_players=self._extract_best_num_players(game),
            bgg_id=game["bggId"],
            bgg_url=f"{BGG_GAME_URL}/{game['bggId']}",
            description=self._extract_description(game),
            id=game["id"],
            image=game["photoUrl"],
            max_play_time=game["playtimeMax"],
            max_players=game["playersMax"],
            min_play_time=game["playtimeMin"],
            min_players=game["playersMin"],
            name=game["title"],
            playing_time=game["playtimeMax"],
            source=TESERA,
            statistics=self._build_game_statistics(game_info),
            url=game["teseraUrl"],
            year_published=game["year"],
        )

    @staticmethod
    def _extract_description(game: dict) -> str:
        """Extract game description"""
        description = game["description"] if "description" in game else game["descriptionShort"]
        description_without_html_tags = clean_html(description)
        unescaped = html.unescape(description_without_html_tags)
        removed_eol = unescaped.replace("\r\n", " ")
        return removed_eol.strip()

    @staticmethod
    def _extract_best_num_players(game: dict) -> str:
        """Extract best number of players"""
        min_recommended = game["playersMinRecommend"]
        max_recommended = game["playersMaxRecommend"]
        if min_recommended == max_recommended:
            return min_recommended
        return f"{min_recommended},{max_recommended}"

    @classmethod
    def _build_game_statistics(cls, game_info: dict) -> GameStatistic:
        """Build game statistics"""
        return GameStatistic(
            avg_rate=game_info["game"]["bggRating"],
            ranks=[],
            weight=NOT_AVAILABLE,
        )
