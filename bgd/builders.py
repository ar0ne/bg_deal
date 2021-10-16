"""
App builders
"""
import abc
from typing import List, Optional

from libbgg.infodict import InfoDict

from bgd.constants import BELARUS, KUFAR, ONLINER, OZBY, OZON, WILDBERRIES
from bgd.responses import (
    GameDetailsResult,
    GameLocation,
    GameOwner,
    GameRank,
    GameSearchResult,
    GameStatistic,
    Price,
)
from bgd.utils import convert_byn_to_usd, remove_backslashes


class GameDetailsResultBuilder:
    """Builder for GameDetailsResult"""

    @classmethod
    def from_game_info(cls, game_info: InfoDict) -> GameDetailsResult:
        """Build details result for the game"""
        item = game_info.get("items").get("item")
        return GameDetailsResult(
            description=item.get("description")["TEXT"],
            id=item.get("id"),
            image=item.get("image")["TEXT"],
            max_play_time=item.get("maxplaytime")["value"],
            max_players=item.get("maxplayers")["value"],
            min_play_time=item.get("minplaytime")["value"],
            min_players=item.get("minplayers")["value"],
            name=cls._get_game_name(item),
            playing_time=item.get("playingtime")["value"],
            statistics=cls._build_game_statistics(item.get("statistics")),
            year_published=item.get("yearpublished")["value"],
        )

    @classmethod
    def _get_game_name(cls, game_info: InfoDict) -> str:
        """Get game name"""
        if isinstance(game_info["name"], list):
            return next(
                filter(lambda n: n.get("type") == "primary", game_info["name"])
            )["value"]
        return game_info["name"]["value"]

    @classmethod
    def _build_game_statistics(cls, statistics: InfoDict) -> GameStatistic:
        """Build game statistics info"""
        ranks = statistics.get("ratings").get("ranks")
        return GameStatistic(
            avg_rate=statistics["ratings"]["average"]["value"],
            ranks=cls._build_game_ranks(ranks),
        )

    @classmethod
    def _build_game_ranks(cls, ranks: InfoDict) -> List[GameRank]:
        game_ranks = ranks["rank"]
        if not isinstance(game_ranks, list):
            game_ranks = [game_ranks]
        return [
            GameRank(
                name=rank["name"],
                value=rank["value"],
            )
            for rank in game_ranks
        ]


class GameSearchResultBuilder:
    @classmethod
    @abc.abstractmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Build game search result from search result"""


class GameSearchResultKufarBuilder(GameSearchResultBuilder):
    """builder for GameSearchResult from Kufar data source"""

    IMAGE_URL = "https://yams.kufar.by/api/v1/kufar-ads/images/{}/{}.jpg?rule=gallery"

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Builds GameSearchResult from search result"""
        return GameSearchResult(
            description="",  # @TODO: how to get it?
            images=cls._extract_images(search_result),
            location=cls._extract_product_location(search_result),
            owner=cls._extract_owner_info(search_result),
            price=cls._extract_price(search_result),
            source=KUFAR,
            subject=search_result.get("subject"),
            url=search_result.get("ad_link"),
        )

    @staticmethod
    def _extract_price(ad_item: dict) -> Price:
        """Extract ad price"""
        return Price(
            byn=int(ad_item.get("price_byn")),
            usd=int(ad_item.get("price_usd")),
        )

    @classmethod
    def _extract_images(cls, ad_item: dict) -> list:
        """Extracts ad images"""
        return [
            cls.IMAGE_URL.format(img.get("id")[:2], img.get("id"))
            for img in ad_item.get("images")
            if img.get("yams_storage")
        ]

    @classmethod
    def _extract_product_location(cls, ad_item: dict) -> GameLocation:
        """Extract location of item"""
        params = ad_item.get("ad_parameters")
        return GameLocation(
            area=cls._extract_ad_area(params) or "",
            city=cls._extract_ad_city(params) or "",
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
    def _extract_owner_info(ad_item: dict) -> GameOwner:
        """Extract info about ads owner"""
        name = [
            v
            for acc_param in ad_item.get("account_parameters")
            for k, v in acc_param.items()
            if k == "v"
        ]
        return GameOwner(
            id=ad_item.get("account_id"),
            name=" ".join(name),
        )


class GameSearchResultWildberriesBuilder(GameSearchResultBuilder):
    """Build GameSearchResult for Wildberrries datasource"""

    ITEM_URL = "https://by.wildberries.ru/catalog/{}/detail.aspx"
    IMAGE_URL = "https://images.wbstatic.net/big/new/{}0000/{}-1.jpg"

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Build game search result"""
        return GameSearchResult(
            description="",
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=WILDBERRIES,
            subject=cls._extract_subject(search_result),
            url=cls._extract_url(search_result),
        )

    @staticmethod
    def _extract_price(product: dict) -> Price:
        """Extract prices for product in different currencies"""
        # @todo: currently I hardcoded "currency" in client, and exchange rate
        price_in_byn = product.get("salePriceU")
        return Price(byn=price_in_byn, usd=convert_byn_to_usd(price_in_byn))

    @classmethod
    def _extract_url(cls, product: dict) -> str:
        """Extract url to product"""
        return cls.ITEM_URL.format(product.get("id"))

    @classmethod
    def _extract_images(cls, product: dict) -> list:
        """Extract product images"""
        product_id = str(product.get("id"))
        return [cls.IMAGE_URL.format(product_id[:4], product_id)]

    @staticmethod
    def _extract_subject(product: dict) -> str:
        """Extract product subject"""
        return f"{product.get('brand')} / {product.get('name')}"


class GameSearchResultOzonBuilder(GameSearchResultBuilder):
    """Builder for game search results from Ozon"""

    ITEM_URL = "https://ozon.ru"

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Builds game search result from ozon data source search result"""
        return GameSearchResult(
            description="",  # @TODO: how to get it?
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=OZON,
            subject=cls._extract_subject(search_result),
            url=cls._extract_url(search_result),
        )

    @classmethod
    def _extract_url(cls, item: dict) -> Optional[str]:
        """Extract url"""
        url = item.get("action").get("link")
        if not url:
            return
        return cls.ITEM_URL + url

    @staticmethod
    def _extract_price(item: dict) -> Optional[Price]:
        """Extract item prices in cents"""
        main_state = item.get("mainState", [])
        price_state = next(filter(lambda it: it.get("id") == "atom", main_state))
        if not price_state:
            return
        price = price_state.get("atom").get("price").get("price")
        if not price:
            return

        price_in_byn = int(100 * float(price.split()[0].replace(",", ".")))
        return Price(byn=price_in_byn, usd=convert_byn_to_usd(price_in_byn))

    @staticmethod
    def _extract_images(item: dict) -> list:
        """Extract images"""
        return item.get("tileImage").get("images", [])

    @staticmethod
    def _extract_subject(item: dict) -> str:
        """Extract item subject"""
        main_state = item.get("mainState", [])
        name_state = next(filter(lambda it: it.get("id") == "name", main_state))
        if not name_state:
            return ""
        return name_state.get("atom").get("textAtom").get("text", "")


class GameSearchResultOzByBuilder(GameSearchResultBuilder):
    """GameSearchResult Builder for oz.by"""

    GAME_URL = "https://oz.by/boardgames/more{}.html"

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Builds game search result from ozon data source search result"""
        return GameSearchResult(
            description=cls._extract_description(search_result),
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=OZBY,
            subject=cls._extract_subject(search_result),
            url=cls._extract_url(search_result),
        )

    @staticmethod
    def _extract_images(item: dict) -> list[str]:
        """Get image of the game"""
        return [item.get("attributes").get("main_image").get("200")]

    @staticmethod
    def _extract_price(item: dict) -> Optional[Price]:
        """Extract game prices"""
        price = item.get("attributes").get("cost").get("decimal")
        if not price:
            return
        return Price(byn=price * 100, usd=convert_byn_to_usd(price * 100))

    @staticmethod
    def _extract_subject(item: dict) -> str:
        """Extracts subject"""
        return item.get("attributes").get("title")

    @classmethod
    def _extract_url(cls, item: dict) -> str:
        """Extracts item url"""
        return cls.GAME_URL.format(item.get("id"))

    @staticmethod
    def _extract_description(item: dict) -> str:
        """Extract item description"""
        return item.get("attributes").get("small_desc")


class GameSearchResultOnlinerBuilder(GameSearchResultBuilder):
    """GameSearchResult builder for search results from onliner.by"""

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Builds game search result from ozon data source search result"""
        return GameSearchResult(
            description=search_result.get("description"),
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=ONLINER,
            subject=search_result.get("name"),
            url=cls._extract_url(search_result),
        )

    @staticmethod
    def _extract_price(product: dict) -> Optional[Price]:
        """Extract product price"""
        price = product.get("prices")
        if not price:
            return
        price_in_byn = price.get("price_min").get("amount")
        price_cents = int(float(price_in_byn) * 100)
        return Price(byn=price_cents, usd=convert_byn_to_usd(price_cents))

    @staticmethod
    def _extract_url(product: dict) -> str:
        """Extract product page url"""
        return remove_backslashes(product.get("html_url", ""))

    @staticmethod
    def _extract_images(product: dict) -> list:
        """Extract product images"""
        image_url = remove_backslashes(product.get("images").get("header"))
        return [f"https:{image_url}"]
