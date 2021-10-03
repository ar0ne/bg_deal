"""
App Services
"""
import math
from typing import List, Optional, Union

from bgd.clients import ApiClient
from bgd.responses import SearchLocation, SearchOwner, SearchResponseItem

BELARUS = "Belarus"
KUFAR = "Kufar"
WILDBERRIES = "Wildberries"


class KufarSearchService:
    """Service for work with Kufar api"""

    def __init__(self, client: ApiClient, game_category_id: Union[str, int]) -> None:
        """Init Search Service"""
        self._client = client
        self.game_category_id = game_category_id

    def search_games(self, game_name: str) -> List[SearchResponseItem]:
        """Search ads by game name"""
        ads = self._client.search(game_name, {"category": self.game_category_id})
        return [self._format_ads(ad) for ad in ads.response.get("ads")]

    def _format_ads(self, ad_item: dict) -> SearchResponseItem:
        """Convert ads to internal data format"""
        return SearchResponseItem(
            images=self._extract_images(ad_item),
            location=self._extract_product_location(ad_item),
            owner=self._extract_owner_info(ad_item),
            prices=self._extract_prices(ad_item),
            source=KUFAR,
            url=ad_item.get("ad_link"),
        )

    @staticmethod
    def _extract_prices(ad_item: dict) -> list:
        """Extract ad prices in different currencies (BYN, USD)"""
        return [
            {"byn": int(ad_item.get("price_byn"))},
            {"usd": int(ad_item.get("price_usd"))},
        ]

    def _extract_images(self, ad_item: dict) -> list:
        """Extracts ad images"""
        # todo: extract images for kufar service
        return []

    def _extract_product_location(self, ad_item: dict) -> SearchLocation:
        """Extract location of item"""
        params = ad_item.get("ad_parameters")
        return SearchLocation(
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

    @staticmethod
    def _extract_ad_area(ad_params: list) -> Optional[str]:
        """Extract ads area"""
        for param in ad_params:
            if param.get("pu") == "ar":
                return param.get("vl")

    @staticmethod
    def _extract_owner_info(ad_item: dict) -> SearchOwner:
        """Extract info about ads owner"""
        name = [
            v
            for acc_param in ad_item.get("account_parameters")
            for k, v in acc_param.items()
            if k == "v"
        ]
        return SearchOwner(
            id=ad_item.get("account_id"),
            name=" ".join(name),
            phone="",
        )


class WildberriesSearchService:
    """Service for work with Wildberries api"""

    def __init__(self, client: ApiClient, game_category_id: Union[str, int]) -> None:
        """Init Search Service"""
        self._client = client
        self.game_category_id = game_category_id

    def search_games(self, game_name: str) -> List[SearchResponseItem]:
        items = self._client.search(game_name)
        return [
            self._format_product(product)
            for product in items.response.get("data", {}).get("products")
            if product.get("subjectId") == self.game_category_id
        ]

    def _format_product(self, product: dict) -> SearchResponseItem:
        """Convert ads to internal data format"""
        return SearchResponseItem(
            images=self._extract_images(product),
            location=None,
            owner=None,
            prices=self._extract_prices(product),
            source=WILDBERRIES,
            url=self._extract_url(product),
        )

    def _extract_prices(self, product: dict) -> list:
        """Extract prices for product in different currencies"""
        # @todo: currently I hardcoded "currency" in client, and exchange rate
        price_in_byn = product.get("salePriceU")
        return [
            {"byn": price_in_byn},
            {"usd": math.floor(price_in_byn * 100 / 253)},
        ]

    def _extract_url(self, product: dict) -> str:
        """Extract url to product"""
        # todo: clean up
        return f"https://by.wildberries.ru/catalog/{product.get('id')}/detail.aspx"

    def _extract_images(self, product: dict) -> list:
        """Extract product images"""
        # @todo: extract images
        return []
