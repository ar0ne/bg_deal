"""
App containers
"""
import os

from dependency_injector import containers, providers
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette.templating import Jinja2Templates
from starlette_json import ORJsonMiddleware, ORJsonResponse

from bgd.services.apis.bcse import BCSECurrencyExchangeRateResultBuilder, BCSEExchangepiClient
from bgd.services.apis.bgg import (
    BGGGameDetailsResultFactory,
    BoardGameGeekApiClient,
    BoardGameGeekGameInfoService,
)
from bgd.services.apis.crowdgames import (
    CrowdGamesApiClient,
    CrowdGamesGameSearchResultFactory,
    CrowdGamesSearchService,
)
from bgd.services.apis.currency_exchange import CurrencyExchangeRateService
from bgd.services.apis.fifth_element import (
    FifthElementApiClient,
    FifthElementGameSearchResultFactory,
    FifthElementSearchService,
)
from bgd.services.apis.hobbygames import (
    HobbyGamesApiClient,
    HobbyGamesGameSearchResultFactory,
    HobbyGamesSearchService,
)
from bgd.services.apis.kufar import KufarApiClient, KufarGameSearchResultFactory, KufarSearchService
from bgd.services.apis.lavkaigr import (
    LavkaIgrApiClient,
    LavkaIgrGameSearchResultFactory,
    LavkaIgrSearchService,
)
from bgd.services.apis.onliner import (
    OnlinerApiClient,
    OnlinerGameSearchResultFactory,
    OnlinerSearchService,
)
from bgd.services.apis.ozby import OzByApiClient, OzByGameSearchResultFactory, OzBySearchService
from bgd.services.apis.ozon import OzonApiClient, OzonGameSearchResultFactory, OzonSearchService
from bgd.services.apis.tesera import (
    TeseraApiClient,
    TeseraGameDetailsResultFactory,
    TeseraGameInfoService,
)
from bgd.services.apis.twenty_first_vek import (
    TwentyFirstVekApiClient,
    TwentyFirstVekGameSearchResultFactory,
    TwentyFirstVekSearchService,
)
from bgd.services.apis.vkontakte import (
    VkontakteApiClient,
    VKontakteGameSearchResultFactory,
    VkontakteSearchService,
)
from bgd.services.apis.wildberries import (
    WildberriesApiClient,
    WildberriesGameSearchResultFactory,
    WildberriesSearchService,
)
from bgd.services.apis.znaemigraem import (
    ZnaemIgraemApiClient,
    ZnaemIgraemGameSearchResultFactory,
    ZnaemIgraemSearchService,
)
from bgd.services.base import GameDealsSearchFacade, SimpleSuggestGameService
from bgd.utils import ORJsonCoder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# pylint: disable=I1101
class ApplicationContainer(containers.DeclarativeContainer):
    """App container"""

    config = providers.Configuration()
    coder = providers.Singleton(ORJsonCoder)
    templates = providers.Factory(
        Jinja2Templates,
        directory=config.templates.dir,
    )
    bgg_service = providers.Singleton(
        BoardGameGeekGameInfoService,
        client=providers.Singleton(BoardGameGeekApiClient),
        result_factory=providers.Singleton(BGGGameDetailsResultFactory),
    )
    tesera_service = providers.Singleton(
        TeseraGameInfoService,
        client=providers.Singleton(TeseraApiClient),
        result_factory=providers.Singleton(TeseraGameDetailsResultFactory),
    )
    nb_exchange_rate_service = providers.Singleton(
        CurrencyExchangeRateService,
        client=providers.Singleton(BCSEExchangepiClient),
        result_builder=providers.Singleton(BCSECurrencyExchangeRateResultBuilder),
    )
    kufar_search_service = providers.Singleton(
        KufarSearchService,
        client=providers.Singleton(KufarApiClient),
        result_factory=providers.Singleton(KufarGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.kufar.game_category_id,
    )
    wildberreis_search_service = providers.Singleton(
        WildberriesSearchService,
        client=providers.Singleton(WildberriesApiClient),
        result_factory=providers.Singleton(WildberriesGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.wildberries.game_category_id,
    )
    ozon_search_service = providers.Singleton(
        OzonSearchService,
        client=providers.Singleton(OzonApiClient),
        result_factory=providers.Singleton(OzonGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.ozon.game_category_id,
    )
    ozby_search_service = providers.Singleton(
        OzBySearchService,
        client=providers.Singleton(OzByApiClient),
        result_factory=providers.Singleton(OzByGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.ozby.game_category_id,
    )
    onliner_search_service = providers.Singleton(
        OnlinerSearchService,
        client=providers.Singleton(OnlinerApiClient),
        result_factory=providers.Singleton(OnlinerGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    twenty_first_vek_service = providers.Singleton(
        TwentyFirstVekSearchService,
        client=providers.Singleton(TwentyFirstVekApiClient),
        result_factory=providers.Singleton(TwentyFirstVekGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    fifth_element_service = providers.Singleton(
        FifthElementSearchService,
        client=providers.Singleton(FifthElementApiClient),
        result_factory=providers.Singleton(FifthElementGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.fifthelement.game_category_id,
        search_app_id=config.fifthelement.search_app_id,
    )
    vk_service = providers.Singleton(
        VkontakteSearchService,
        client=providers.Singleton(VkontakteApiClient),
        result_factory=providers.Singleton(VKontakteGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        group_id=config.vk.group_id,
        group_name=config.vk.group_name,
        api_token=config.vk.api_token,
        api_version=config.vk.api_version,
        limit=config.vk.limit,
    )
    znaem_igraem_service = providers.Singleton(
        ZnaemIgraemSearchService,
        client=providers.Singleton(ZnaemIgraemApiClient),
        result_factory=providers.Singleton(ZnaemIgraemGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    hobbygames = providers.Singleton(
        HobbyGamesSearchService,
        client=providers.Singleton(HobbyGamesApiClient),
        result_factory=providers.Singleton(HobbyGamesGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    lavkaigr = providers.Singleton(
        LavkaIgrSearchService,
        client=providers.Singleton(LavkaIgrApiClient),
        result_factory=providers.Singleton(LavkaIgrGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    crowdgames = providers.Singleton(
        CrowdGamesSearchService,
        client=providers.Singleton(CrowdGamesApiClient),
        result_factory=providers.Singleton(CrowdGamesGameSearchResultFactory),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    data_sources = providers.List(
        crowdgames,
        fifth_element_service,
        hobbygames,
        kufar_search_service,
        lavkaigr,
        onliner_search_service,
        ozby_search_service,
        ozon_search_service,
        twenty_first_vek_service,
        vk_service,
        wildberreis_search_service,
        znaem_igraem_service,
    )
    game_search_facade = providers.Singleton(
        GameDealsSearchFacade,
        data_sources=data_sources,
        json_coder=coder,
    )
    suggest_game_service = providers.Singleton(
        SimpleSuggestGameService,
        games=config.app.suggested_games,
    )
    redis = providers.Singleton(
        aioredis.from_url,
        config.cache.url,
        encoding="utf8",
        decode_responses=True,
    )
    cache_backend = providers.Selector(
        config.cache.backend,
        in_memory=providers.Singleton(InMemoryBackend),
        redis=providers.Singleton(RedisBackend, redis),
    )
    middlewares = providers.List(
        providers.Factory(lambda: ORJsonMiddleware),
    )
    get_response_class = providers.Factory(lambda: ORJsonResponse)
