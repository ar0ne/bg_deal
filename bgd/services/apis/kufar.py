"""
Kufar.by API Client
"""
from typing import List, Optional

from bgd.constants import BELARUS, KUFAR
from bgd.responses import GameLocation, GameOwner, GameSearchResult, Price
from bgd.services.abc import GameSearchResultFactory
from bgd.services.api_clients import JsonHttpApiClient
from bgd.services.base import GameSearchService
from bgd.services.constants import GET
from bgd.services.responses import APIResponse


class KufarApiClient(JsonHttpApiClient):
    """Client for Kufar API"""

    BASE_URL = "https://cre-api.kufar.by"
    SEARCH_PATH = "/ads-search/v1/engine/v1/search/rendered-paginated"
    CATEGORIES_PATH = "/category_tree/v1/category_tree"

    async def search(self, query: str, options: Optional[dict] = None) -> APIResponse:
        """Search kufar ads by query and category"""

        url = f"{self.SEARCH_PATH}?query={query}"

        if options:
            if options.get("category"):
                url += f"&cat={options['category']}"
            if options.get("language"):
                url += f"&lang={options['language']}"
            size = options.get("size", 10)
            if size:
                url += f"&size={size}"

        return await self.connect(GET, self.BASE_URL, url)

    async def get_all_categories(self) -> APIResponse:
        """Get all existing categories"""
        return await self.connect(GET, self.BASE_URL, self.CATEGORIES_PATH)


class KufarSearchService(GameSearchService):
    """Service for work with Kufar api"""

    async def do_search(self, query: str, *args, **kwargs) -> List[GameSearchResult]:
        """Search ads by game name"""
        search_response = await self._client.search(query, {"category": self._game_category_id})
        products = self.filter_results(search_response.response["ads"])
        return self.build_results(products)

    @property
    def result_factory(self) -> GameSearchResultFactory:
        """Creates result factory"""
        return KufarGameSearchResultFactory()


class KufarGameSearchResultFactory:
    """builder for GameSearchResult from Kufar data source"""

    IMAGE_URL = "https://yams.kufar.by/api/v1/kufar-ads/images/{}/{}.jpg?rule=gallery"
    USER_URL = "https://www.kufar.by/user/{}"

    def create(self, search_result: dict) -> GameSearchResult:
        """Builds GameSearchResult from search result"""
        return GameSearchResult(
            description="",  # @TODO: how to get it?
            images=self._extract_images(search_result),
            location=self._extract_product_location(search_result),
            owner=self._extract_owner_info(search_result),
            prices=[self._extract_price(search_result)],
            source=KUFAR,
            subject=search_result.get("subject"),
            url=search_result.get("ad_link"),
        )

    @staticmethod
    def _extract_price(ad_item: dict) -> Optional[Price]:
        """Extract ad price"""
        return Price(amount=int(ad_item["price_byn"]))

    def _extract_images(self, ad_item: dict) -> list:
        """Extracts ad images"""
        return [
            self.IMAGE_URL.format(img.get("id")[:2], img.get("id"))
            for img in ad_item["images"]
            if img.get("yams_storage")
        ]

    def _extract_product_location(self, ad_item: dict) -> GameLocation:
        """Extract location of item"""
        params: list = ad_item["ad_parameters"]
        return GameLocation(
            area=self._extract_ad_area(params) or "",
            city=self._extract_ad_city(params) or "",
            country=BELARUS,
        )

    @staticmethod
    def _extract_ad_city(ad_params: list) -> Optional[str]:
        """Extracts add city"""
        for param in ad_params:
            if param.get("pu") == "rgn":
                return param.get("vl")
        return None

    @staticmethod
    def _extract_ad_area(ad_params: list) -> Optional[str]:
        """Extract ads area"""
        for param in ad_params:
            if param.get("pu") == "ar":
                return param.get("vl")
        return None

    @classmethod
    def _extract_owner_info(cls, ad_item: dict) -> GameOwner:
        """Extract info about ads owner"""
        name = [
            v
            for acc_param in ad_item["account_parameters"]
            for k, v in acc_param.items()
            if k == "v"
        ]
        user_id = ad_item.get("account_id")
        if not user_id:
            user_id = ""
        return GameOwner(id=user_id, name=" ".join(name), url=cls.USER_URL.format(user_id))
