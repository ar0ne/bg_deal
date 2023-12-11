"""
App utilities.
"""
import logging
from typing import Any

import orjson
from fastapi.encoders import jsonable_encoder
from fastapi_cache import Coder

log = logging.getLogger(__name__)


# pylint: disable=no-member
class ORJsonCoder(Coder):
    """orjson coder"""

    @classmethod
    def encode(cls, value: Any) -> str:
        """serialize python object to json-bytes"""
        return orjson.dumps(value, default=jsonable_encoder).decode("utf-8")

    @classmethod
    def decode(cls, value: Any) -> Any:
        """deserializes JSON to Python objects"""
        try:
            return orjson.loads(value)
        except orjson.JSONDecodeError:
            log.warning("Unable to decode %s", value)
        return None
