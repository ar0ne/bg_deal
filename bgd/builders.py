"""
App builders
"""
from libbgg.infodict import InfoDict

from bgd.responses import GameDetailsResult, GameRank, GameStatistic


class GameDetailsResultBuilder:
    """Builder for GameDetailsResult"""

    @classmethod
    def from_game_info(cls, game_info: InfoDict) -> GameDetailsResult:
        """Build details result for the game"""
        item = game_info.get("items", {}).get("item", {})
        return GameDetailsResult(
            description=item.get("description")["TEXT"],
            id=item.get("id"),
            image=item.get("image")["TEXT"],
            max_play_time=item.get("maxplaytime")["value"],
            max_players=item.get("maxplayers")["value"],
            min_play_time=item.get("minplaytime")["value"],
            min_players=item.get("minplayers")["value"],
            name=next(
                filter(lambda n: n.get("type") == "primary", item.get("name", []))
            )["value"],
            playing_time=item.get("playingtime")["value"],
            statistics=cls._build_game_statistics(item.get("statistics")),
            year_published=item.get("yearpublished")["value"],
        )

    @classmethod
    def _build_game_statistics(cls, statistics: InfoDict) -> GameStatistic:
        """Build game statistics info"""
        return GameStatistic(
            avg_rate=statistics["ratings"]["average"]["value"],
            ranks=[
                cls._build_game_ranks(rank)
                for rank in statistics.get("ratings", {})
                .get("ranks", {})
                .get("rank", [])
                if rank
            ],
        )

    @classmethod
    def _build_game_ranks(cls, rank: InfoDict) -> GameRank:
        return GameRank(
            name=rank.get("name"),
            value=rank.get("value"),
        )
