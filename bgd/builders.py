"""
App builders
"""
import abc
import html
from typing import Generator, List, Optional, Tuple

from libbgg.infodict import InfoDict

from bgd.constants import (
    BELARUS,
    FIFTHELEMENT,
    KUFAR,
    ONLINER,
    OZBY,
    OZON,
    TWENTYFIRSTVEK,
    WILDBERRIES,
)
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

    GAME_URL = "https://boardgamegeek.com/boardgame"

    @classmethod
    def from_game_info(cls, game_info: InfoDict) -> GameDetailsResult:
        """Build details result for the game"""
        item = game_info.get("items").get("item")
        return GameDetailsResult(
            best_num_players=cls._extract_best_num_players(item),
            description=cls._extract_description(item),
            id=item["id"],
            image=item["image"]["TEXT"],
            max_play_time=item["maxplaytime"]["value"],
            max_players=item["maxplayers"]["value"],
            min_play_time=item["minplaytime"]["value"],
            min_players=item["minplayers"]["value"],
            name=cls._get_game_name(item),
            playing_time=item["playingtime"]["value"],
            statistics=cls._build_game_statistics(item["statistics"]),
            url=cls._build_game_url(item),
            year_published=item["yearpublished"]["value"],
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
        ratings = statistics["ratings"]
        ranks = ratings["ranks"]
        return GameStatistic(
            avg_rate=ratings["average"]["value"],
            ranks=cls._build_game_ranks(ranks),
            weight=ratings["averageweight"]["value"],
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

    @classmethod
    def _build_game_url(cls, item: InfoDict) -> str:
        """Build url to the game on bgg website"""
        return f"{cls.GAME_URL}/{item['id']}"

    @classmethod
    def _extract_best_num_players(cls, item: InfoDict) -> Optional[str]:
        """Extracts best number of players"""
        poll = item.get("poll")
        if not poll:
            return None
        suggested_num_players = next(
            (p["results"] for p in poll if p["name"] == "suggested_numplayers"), False
        )
        best_votes = cls._extract_best_votes(suggested_num_players)  # type: ignore
        highest_votes = max(best_votes, key=lambda bv: int(bv[1]))
        return highest_votes[0] if highest_votes and highest_votes[1] != "0" else None

    @staticmethod
    def _extract_best_votes(votes: list) -> Generator[Tuple[str, str], None, None]:
        """Yields Tuple of num_players and value of 'best' votes"""
        for vote in votes:
            best_vote_num = next(
                (
                    value["numvotes"]
                    for value in vote["result"]
                    if value["value"] == "Best"
                ),
                False,
            )
            yield vote["numplayers"], best_vote_num  # type: ignore

    @staticmethod
    def _extract_description(item: InfoDict) -> str:
        """Extract game description"""
        original_text = item["description"]["TEXT"]
        unescaped_text = html.unescape(original_text)
        return unescaped_text.replace("&#10;", "")


class GameSearchResultBuilder:
    """Base builder class for game search result"""

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
    def _extract_price(ad_item: dict) -> Optional[Price]:
        """Extract ad price"""
        return Price(
            byn=int(ad_item["price_byn"]),
            usd=int(ad_item["price_usd"]),
        )

    @classmethod
    def _extract_images(cls, ad_item: dict) -> list:
        """Extracts ad images"""
        return [
            cls.IMAGE_URL.format(img.get("id")[:2], img.get("id"))
            for img in ad_item["images"]
            if img.get("yams_storage")
        ]

    @classmethod
    def _extract_product_location(cls, ad_item: dict) -> GameLocation:
        """Extract location of item"""
        params: list = ad_item["ad_parameters"]
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
        return None

    @staticmethod
    def _extract_ad_area(ad_params: list) -> Optional[str]:
        """Extract ads area"""
        for param in ad_params:
            if param.get("pu") == "ar":
                return param.get("vl")
        return None

    @staticmethod
    def _extract_owner_info(ad_item: dict) -> GameOwner:
        """Extract info about ads owner"""
        name = [
            v
            for acc_param in ad_item["account_parameters"]
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
        price_in_byn: int = product["salePriceU"]
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
        url = item["action"]["link"]
        if not url:
            return None
        return cls.ITEM_URL + url

    @staticmethod
    def _extract_price(item: dict) -> Optional[Price]:
        """Extract item prices in cents"""
        main_state = item.get("mainState", [])
        price_state = next(filter(lambda it: it.get("id") == "atom", main_state))
        if not price_state:
            return None
        price = price_state.get("atom").get("price").get("price")
        if not price:
            return None

        price_in_byn = int(100 * float(price.split()[0].replace(",", ".")))
        return Price(byn=price_in_byn, usd=convert_byn_to_usd(price_in_byn))

    @staticmethod
    def _extract_images(item: dict) -> list:
        """Extract images"""
        return item["tileImage"]["images"] or []

    @staticmethod
    def _extract_subject(item: dict) -> str:
        """Extract item subject"""
        main_state = item.get("mainState", [])
        name_state = next(filter(lambda it: it["id"] == "name", main_state))
        if not name_state:
            return ""
        name = name_state["atom"]["textAtom"]["text"] or ""
        return html.unescape(name)


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
        return [item["attributes"]["main_image"]["200"]]

    @staticmethod
    def _extract_price(item: dict) -> Optional[Price]:
        """Extract game prices"""
        price = item["attributes"]["cost"]["decimal"]
        if not price:
            return None
        return Price(byn=price * 100, usd=convert_byn_to_usd(price * 100))

    @staticmethod
    def _extract_subject(item: dict) -> str:
        """Extracts subject"""
        return item["attributes"]["title"]

    @classmethod
    def _extract_url(cls, item: dict) -> str:
        """Extracts item url"""
        return cls.GAME_URL.format(item["id"])

    @staticmethod
    def _extract_description(item: dict) -> str:
        """Extract item description"""
        return item["attributes"].get("small_desc")


class GameSearchResultOnlinerBuilder(GameSearchResultBuilder):
    """GameSearchResult builder for search results from onliner.by"""

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Builds game search result from ozon data source search result"""
        return GameSearchResult(
            description=search_result["description"],
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=ONLINER,
            subject=search_result["name"],
            url=cls._extract_url(search_result),
        )

    @staticmethod
    def _extract_price(product: dict) -> Optional[Price]:
        """Extract product price"""
        price = product.get("prices")
        if not price:
            return None
        price_in_byn = price["price_min"]["amount"]
        price_cents = int(float(price_in_byn) * 100)
        return Price(byn=price_cents, usd=convert_byn_to_usd(price_cents))

    @staticmethod
    def _extract_url(product: dict) -> str:
        """Extract product page url"""
        return remove_backslashes(product.get("html_url", ""))

    @staticmethod
    def _extract_images(product: dict) -> list:
        """Extract product images"""
        image_url = remove_backslashes(product["images"]["header"])
        return [f"https:{image_url}"]


class GameSearchResultTwentyFirstVekBuilder(GameSearchResultBuilder):
    """Builder for 21vek"""

    BASE_URL = "https://21vek.by"

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        return GameSearchResult(
            description=search_result["highlighted"],
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=TWENTYFIRSTVEK,
            subject=search_result["name"],
            url=cls._extract_url(search_result),
        )

    @staticmethod
    def _extract_price(product: dict) -> Price:
        """Extract price"""
        # "price": "60,00 р."
        price = product["price"]
        price = price.split(" ")[0]
        price = int(price.replace(",", ""))
        return Price(byn=price, usd=convert_byn_to_usd(price))

    @classmethod
    def _extract_url(cls, product: dict) -> str:
        """Extract product url"""
        return f"{cls.BASE_URL}{product['url']}"

    @staticmethod
    def _extract_images(product: dict) -> list[str]:
        """Extract product images"""
        pic_url = product["picture"]
        bigger_img = pic_url.replace("preview_s", "preview_b")
        return [bigger_img]


class GameSearchResultFifthElementBuilder(GameSearchResultBuilder):
    """Builder for GameSearch results from 5element"""

    BASE_URL = "https://5element.by"

    @classmethod
    def from_search_result(cls, search_result: dict) -> GameSearchResult:
        """Build search result"""
        return GameSearchResult(
            description="",
            images=cls._extract_images(search_result),
            location=None,
            owner=None,
            price=cls._extract_price(search_result),
            source=FIFTHELEMENT,
            subject=search_result["name"],
            url=cls._extract_url(search_result),
        )

    @staticmethod
    def _extract_images(product: dict) -> list[str]:
        """Extract product images"""
        return [product["picture"]]

    @staticmethod
    def _extract_price(product: dict) -> Optional[Price]:
        """Extract price"""
        price = product["price"] * 100
        return Price(byn=price, usd=convert_byn_to_usd(price))

    @classmethod
    def _extract_url(cls, product: dict) -> str:
        """Extract product url"""
        return f"{cls.BASE_URL}{product['url']}"
