"""
BGG (board game geek) API Client
"""
import html
from typing import Generator, List, Optional, Tuple, Union

from libbgg.infodict import InfoDict

from bgd.constants import BGG
from bgd.responses import GameDetailsResult, GameRank, GameStatistic
from bgd.services.api_clients import XmlHttpApiClient
from bgd.services.base import GameInfoService
from bgd.services.builders import GameDetailsResultBuilder
from bgd.services.constants import GET
from bgd.services.responses import APIResponse
from bgd.services.types import GameAlias

BGG_GAME_URL = "https://boardgamegeek.com/boardgame"


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


class BGGGameDetailsResultBuilder(GameDetailsResultBuilder):
    """Builder for GameDetailsResult"""

    @classmethod
    def build(cls, game_info: InfoDict) -> GameDetailsResult:
        """Build details result for the game"""
        item = game_info.get("items").get("item")
        return GameDetailsResult(
            best_num_players=cls._extract_best_num_players(item),
            bgg_id=item["id"],
            bgg_url=cls._build_game_url(item),
            description=cls._extract_description(item),
            id=item["id"],
            image=item["image"]["TEXT"],
            max_play_time=item["maxplaytime"]["value"],
            max_players=item["maxplayers"]["value"],
            min_play_time=item["minplaytime"]["value"],
            min_players=item["minplayers"]["value"],
            name=cls._get_game_name(item),
            playing_time=item["playingtime"]["value"],
            source=BGG,
            statistics=cls._build_game_statistics(item["statistics"]),
            url=cls._build_game_url(item),
            year_published=item["yearpublished"]["value"],
        )

    @classmethod
    def _get_game_name(cls, game_info: InfoDict) -> str:
        """Get game name"""
        if isinstance(game_info["name"], list):
            return next(
                filter(lambda n: n.get("type") == "primary", game_info["name"])
            )["value"]
        return game_info["name"]["value"]

    @classmethod
    def _build_game_statistics(cls, statistics: InfoDict) -> GameStatistic:
        """Build game statistics info"""
        ratings = statistics["ratings"]
        ranks = ratings["ranks"]
        return GameStatistic(
            avg_rate=ratings["average"]["value"],
            ranks=cls._build_game_ranks(ranks),
            weight=ratings["averageweight"]["value"],
        )

    @classmethod
    def _build_game_ranks(cls, ranks: InfoDict) -> List[GameRank]:
        game_ranks = ranks["rank"]
        if not isinstance(game_ranks, list):
            game_ranks = [game_ranks]
        return [
            GameRank(
                name=rank["name"],
                value=rank["value"],
            )
            for rank in game_ranks
        ]

    @classmethod
    def _build_game_url(cls, item: InfoDict) -> str:
        """Build url to the game on bgg website"""
        return f"{BGG_GAME_URL}/{item['id']}"

    @classmethod
    def _extract_best_num_players(cls, item: InfoDict) -> Optional[str]:
        """Extracts best number of players"""
        poll = item.get("poll")
        if not poll:
            return None
        suggested_num_players = next(
            (p["results"] for p in poll if p["name"] == "suggested_numplayers"), False
        )
        best_votes = cls._extract_best_votes(suggested_num_players)  # type: ignore
        highest_votes = max(best_votes, key=lambda bv: int(bv[1]))
        return highest_votes[0] if highest_votes and highest_votes[1] != "0" else None

    @staticmethod
    def _extract_best_votes(votes: list) -> Generator[Tuple[str, str], None, None]:
        """Yields Tuple of num_players and value of 'best' votes"""
        for vote in votes:
            best_vote_num = next(
                (
                    value["numvotes"]
                    for value in vote["result"]
                    if value["value"] == "Best"
                ),
                False,
            )
            yield vote["numplayers"], best_vote_num  # type: ignore

    @staticmethod
    def _extract_description(item: InfoDict) -> str:
        """Extract game description"""
        original_text = item["description"]["TEXT"]
        unescaped_text = html.unescape(original_text)
        return unescaped_text.replace("&#10;", "")
