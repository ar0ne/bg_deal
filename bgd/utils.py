"""
App utilities.
"""
from typing import Any

import orjson
from fastapi.encoders import jsonable_encoder
from fastapi_cache import Coder


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
