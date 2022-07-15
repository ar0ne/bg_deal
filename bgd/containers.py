"""
App containers
"""
import os

import aioredis
from dependency_injector import containers, providers
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from starlette.templating import Jinja2Templates
from starlette_json import ORJsonMiddleware, ORJsonResponse

from bgd.services.apis.bcse import BCSECurrencyExchangeRateResultBuilder, BCSEExchangepiClient
from bgd.services.apis.bgg import BoardGameGeekApiClient, BoardGameGeekGameInfoService
from bgd.services.apis.crowdgames import CrowdGamesApiClient, CrowdGamesSearchService
from bgd.services.apis.currency_exchange import CurrencyExchangeRateService
from bgd.services.apis.fifth_element import FifthElementApiClient, FifthElementSearchService
from bgd.services.apis.hobbygames import HobbyGamesApiClient, HobbyGamesSearchService
from bgd.services.apis.kufar import KufarApiClient, KufarSearchService
from bgd.services.apis.lavkaigr import LavkaIgrApiClient, LavkaIgrSearchService
from bgd.services.apis.onliner import OnlinerApiClient, OnlinerSearchService
from bgd.services.apis.ozby import OzByApiClient, OzBySearchService
from bgd.services.apis.ozon import OzonApiClient, OzonSearchService
from bgd.services.apis.tesera import TeseraApiClient, TeseraGameInfoService
from bgd.services.apis.twenty_first_vek import TwentyFirstVekApiClient, TwentyFirstVekSearchService
from bgd.services.apis.vkontakte import VkontakteApiClient, VkontakteSearchService
from bgd.services.apis.wildberries import WildberriesApiClient, WildberriesSearchService
from bgd.services.apis.znaemigraem import ZnaemIgraemApiClient, ZnaemIgraemSearchService
from bgd.services.base import SimpleSuggestGameService
from bgd.utils import ORJsonCoder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# pylint: disable=I1101
class ApplicationContainer(containers.DeclarativeContainer):
    """App container"""

    config = providers.Configuration()
    templates = providers.Factory(
        Jinja2Templates,
        directory=config.templates.dir,
    )
    bgg_service = providers.Singleton(
        BoardGameGeekGameInfoService,
        client=providers.Singleton(BoardGameGeekApiClient),
    )
    tesera_service = providers.Singleton(
        TeseraGameInfoService,
        client=providers.Singleton(TeseraApiClient),
    )
    nb_exchange_rate_service = providers.Singleton(
        CurrencyExchangeRateService,
        client=providers.Singleton(BCSEExchangepiClient),
        result_builder=providers.Singleton(BCSECurrencyExchangeRateResultBuilder),
    )
    kufar_search_service = providers.Singleton(
        KufarSearchService,
        client=providers.Singleton(KufarApiClient),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.kufar.game_category_id,
    )
    wildberreis_search_service = providers.Singleton(
        WildberriesSearchService,
        client=providers.Singleton(WildberriesApiClient),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.wildberries.game_category_id,
    )
    ozon_search_service = providers.Singleton(
        OzonSearchService,
        client=providers.Singleton(OzonApiClient),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.ozon.game_category_id,
    )
    ozby_search_service = providers.Singleton(
        OzBySearchService,
        client=providers.Singleton(OzByApiClient),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.ozby.game_category_id,
    )
    onliner_search_service = providers.Singleton(
        OnlinerSearchService,
        client=providers.Singleton(OnlinerApiClient),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    twenty_first_vek_service = providers.Singleton(
        TwentyFirstVekSearchService,
        client=providers.Singleton(TwentyFirstVekApiClient),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    fifth_element_service = providers.Singleton(
        FifthElementSearchService,
        client=providers.Singleton(FifthElementApiClient),
        currency_exchange_rate_converter=nb_exchange_rate_service,
        game_category_id=config.fifthelement.game_category_id,
        search_app_id=config.fifthelement.search_app_id,
    )
    vk_service = providers.Singleton(
        VkontakteSearchService,
        client=providers.Singleton(VkontakteApiClient),
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
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    hobbygames = providers.Singleton(
        HobbyGamesSearchService,
        client=providers.Singleton(HobbyGamesApiClient),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    lavkaigr = providers.Singleton(
        LavkaIgrSearchService,
        client=providers.Singleton(LavkaIgrApiClient),
        currency_exchange_rate_converter=nb_exchange_rate_service,
    )
    crowdgames = providers.Singleton(
        CrowdGamesSearchService,
        client=providers.Singleton(CrowdGamesApiClient),
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
    cache_coder = providers.Singleton(ORJsonCoder)
    middlewares = providers.List(
        providers.Factory(lambda: ORJsonMiddleware),
    )
    get_response_class = providers.Factory(lambda: ORJsonResponse)
