"""
Api client interfaces
"""
import datetime
import json
import logging
from typing import Optional, Protocol, Union

import aiohttp
from aiohttp import ClientResponse
from libbgg.infodict import InfoDict

from bgd.api_clients.responses import (
    APIRequest,
    APIResponse,
    JSONAPIResponse,
    XMLAPIResponse,
)
from bgd.errors import ApiClientError, PageNotFoundError

log = logging.getLogger(__name__)


def handle_response(response: ClientResponse) -> None:
    """Handle response status and raise exception if needed"""
    status = response.status
    if status == 404:
        log.warning("PageNotFound error occurs for response %s", response)
        raise PageNotFoundError(str(response.url))
    if not 200 <= status < 300:
        log.warning("ApiClient error occurs for response %s", response)
        raise ApiClientError(str(status))


class HttpApiClient(Protocol):
    """http api client interface"""

    async def connect(
        self,
        method: str,
        base_url: str,
        path: str,
        body: Optional[str] = None,
        headers: Optional[dict] = None,
    ) -> APIResponse:
        """Connect to api"""
        ...

    @staticmethod
    def prepare_request(**kwargs) -> APIRequest:
        """Prepare request for execution"""
        ...

    @staticmethod
    async def prepare_response(response: ClientResponse) -> APIResponse:
        """Prepare response after execution"""
        ...


class Connector:
    """Simple async http api connector"""

    # pylint: disable=no-member
    async def connect(
        self,
        method: str,
        base_url: str,
        path: str,
        body: Optional[str] = None,
        headers: Optional[dict] = None,
    ) -> APIResponse:
        """Connect Api to resource"""
        async with aiohttp.ClientSession() as session:
            url = base_url + path
            request = self.prepare_request(  # type: ignore
                method=method, url=url, headers=headers, body=body
            )
            async with session.request(**request.to_dict()) as resp:
                handle_response(resp)
                return await self.prepare_response(resp)  # type: ignore


class JSONResource:
    """Json Resource"""

    @staticmethod
    def prepare_request(**kwargs: dict) -> APIRequest:
        """Prepare request to work with JSON resources"""
        kwargs_copy: dict = kwargs.copy()
        body = kwargs_copy.pop("body", None)
        kwargs_copy["json"] = None if not body else json.dumps(body)
        return APIRequest(**kwargs_copy)

    @staticmethod
    async def prepare_response(response: ClientResponse) -> JSONAPIResponse:
        """Prepare response from Json resource"""
        r_json = await response.json(content_type=None)
        return JSONAPIResponse(r_json, response.status)


class XMLResource:
    """XML Resource"""

    @staticmethod
    def prepare_request(**kwargs) -> APIRequest:
        """Prepare request to work with XML resource"""
        kwargs_copy: dict = kwargs.copy()
        kwargs_copy.pop("body", None)
        return APIRequest(**kwargs_copy)

    @staticmethod
    async def prepare_response(response: ClientResponse) -> XMLAPIResponse:
        """Prepare response from XML resource"""
        r_text = await response.text(encoding=None)
        info_dict = InfoDict.xml_to_info_dict(r_text, strip_errors=True)
        return XMLAPIResponse(info_dict, response.status)


class JsonHttpApiClient(JSONResource, Connector):
    """Json Http API client"""


class XmlHttpApiClient(XMLResource, Connector):
    """Xml Http API client"""


class GameSearcher(Protocol):
    """Api client for searching games"""

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search by query"""
        ...


class GameInfoSearcher(Protocol):
    """Api client for game info searching"""

    async def search_game_info(
        self, query: str, options: Optional[dict] = None
    ) -> APIResponse:
        """Search info about game"""
        ...

    async def get_game_details(self, game_alias: Union[str, int]) -> APIResponse:
        """Get info about the game"""
        ...


class CurrencyExchangeRateSearcher(Protocol):
    """Interface for currency exchange rate api's"""

    async def get_currency_exchange_rates(self, on_date: datetime.date) -> APIResponse:
        """Get currency exchange rates"""
        ...