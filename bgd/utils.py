"""
App utilities.
"""
from bgd.responses import GameSearchResult


def game_search_result_price(game: GameSearchResult) -> int:
    """Function for sort game search results by price"""
    if not (game and game.price):
        return 0
    return game.price.amount
