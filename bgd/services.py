"""
App Services
"""
from typing import List, Optional, Union

from bgd.clients import KufarApiClient
from bgd.responses import SearchResponseItem

BELARUS = "Belarus"


class KufarSearchService:
    """Api client for searching game deals"""

    def __init__(self, client: KufarApiClient) -> None:
        """Init Search Service"""
        self._client = client

    def search_game_ads(
        self, game_name: str, game_category_id: Union[str, int]
    ) -> List[SearchResponseItem]:
        """Search ads by game name"""
        ads = self._client.search(game_name, {"category": game_category_id})
        return [self._format_ads(ad) for ad in ads.response.get("ads")]

    def _format_ads(self, ad_item: dict) -> SearchResponseItem:
        """Convert ads to internal data format"""
        return SearchResponseItem(
            images=self._extract_ad_images(ad_item),
            location=self._extract_ad_location(ad_item),
            owner=self._extract_ad_owner_info(ad_item),
            prices=self._extract_ad_prices(ad_item),
            url=ad_item.get("ad_link"),
        )

    @staticmethod
    def _extract_ad_prices(ad_item: dict) -> list:
        """Extract ad prices in different currencies (BYN, USD)"""
        return [
            {"byn": ad_item.get("price_byn")},
            {"usd": ad_item.get("price_usd")},
        ]

    def _extract_ad_images(self, ad_item: dict) -> list:
        """Extracts ad images"""
        # todo: extract images for kufar service
        return []

    def _extract_ad_location(self, ad_item: dict) -> dict:
        """Extract location of item"""
        params = ad_item.get("ad_parameters")
        return {
            "country": BELARUS,
            "city": self._extract_ad_city(params) or "",
            "area": self._extract_ad_area(params) or "",
        }

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
    def _extract_ad_owner_info(ad_item: dict) -> dict:
        """Extract info about ads owner"""
        name = [
            v
            for acc_param in ad_item.get("account_parameters")
            for k, v in acc_param.items()
            if k == "v"
        ]
        return {
            "id": ad_item.get("account_id"),
            "name": " ".join(name),
            "phone": "",
        }
