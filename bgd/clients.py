"""
Api clients
"""
import importlib
import json
from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class APIResponse:
    response: dict
    status: int


class ApiClient:
    """Abstract api client"""

    @abstractmethod
    def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search by query"""


class KufarApiClient(ApiClient):
    """Client for Kufar API"""

    BASE_URL = "cre-api.kufar.by"
    SEARCH_PATH = "/ads-search/v1/engine/v1/search/rendered-paginated"
    CATEGORIES_PATH = "/category_tree/v1/category_tree"

    def __init__(self):
        self.httplib = importlib.import_module("http.client")

    def connect(
        self,
        method: str,
        url: str,
        request_body_dict: str = "",
        headers: Optional[dict] = None,
    ) -> APIResponse:
        connection = self.httplib.HTTPSConnection(self.BASE_URL, port=443)
        headers = headers or {}
        body_str = json.dumps(request_body_dict)
        connection.request(method, url, body_str, headers)
        response = connection.getresponse()
        if not 200 <= response.status < 300:
            # todo: raise error?
            return APIResponse({"error": "something went wrong"}, 500)
        return APIResponse(json.loads(response.read().decode("utf-8")), 200)

    def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search ads by category"""

        url = f"{self.SEARCH_PATH}?query={query}"

        if options.get("category"):
            url += f"&cat={options['category']}"
        if options.get("language"):
            url += f"&lang={options['language']}"

        return self.connect("GET", url)

    def get_all_categories(self) -> APIResponse:
        """Get all existing categories"""
        return self.connect("GET", self.CATEGORIES_PATH)
