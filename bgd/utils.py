"""
App utilities.
"""
import json
import logging
from typing import List

from fastapi import Request

from bgd.responses import GameSearchResult
from bgd.services.base import GameSearchService

logger = logging.getLogger(__name__)


def game_search_result_price(game: GameSearchResult) -> int:
    """Function for sort game search results by price"""
    if not (game and game.price):
        return 0
    return game.price.amount


stream_retry_timeout = 30000  # milliseconds


async def game_deals_finder(
    request: Request,
    game: str,
    data_sources: List[GameSearchService],
):
    """Game finder generator"""
    while True:
        if await request.is_disconnected():
            logger.debug("Request disconnected.")
            break

        for source in data_sources:
            deals = await source.search(game)
            if deals:
                yield {
                    "event": "update",
                    "retry": stream_retry_timeout,
                    "data": json.dumps([d.dict() for d in deals]),
                }

        logger.debug("We processed all data sources. Close connection.")
        yield {
            "event": "end",
            "data": "",
        }
