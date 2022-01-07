"""
App utilities.
"""
import logging
import time
from typing import Any, List

import orjson
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi_cache import Coder

from bgd.services.base import GameSearchService

logger = logging.getLogger(__name__)


STREAM_RETRY_TIMEOUT = 30000  # milliseconds


class ORJsonCoder(Coder):
    """orjson coder"""

    @classmethod
    def encode(cls, value: Any) -> bytes:
        """serialize python object to json-bytes"""
        return orjson.dumps(value, default=jsonable_encoder)  # pylint: disable=no-member

    @classmethod
    def decode(cls, value: Any) -> Any:
        """deserializes JSON to Python objects"""
        return orjson.loads(value)  # pylint: disable=no-member


def serialize_event_data(data: Any) -> str:
    """Convert event data to JSON-string"""
    return orjson.dumps(data).decode("utf-8")  # pylint: disable=no-member


async def game_deals_finder(
    request: Request,
    game: str,
    data_sources: List[GameSearchService],
):
    """Game finder generator"""
    start = time.time()
    while True:
        if await request.is_disconnected():
            logger.debug("Request disconnected.")
            break

        for source in data_sources:
            deals = await source.search(game)
            if deals:
                yield {
                    "event": "update",
                    "retry": STREAM_RETRY_TIMEOUT,
                    "data": serialize_event_data(deals),  # convert to json-string for frontend
                }

        logger.debug("We processed all data sources. Close connection.")
        elapsed_time = f"{time.time() - start:.2f}"
        yield {
            "event": "end",
            "data": serialize_event_data(
                {
                    "time": elapsed_time,
                }
            ),
        }
        break
