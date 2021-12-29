"""
App containers
"""
import os

from dependency_injector import containers, providers
from starlette.templating import Jinja2Templates

from bgd.services.apis.bgg import (
    BGGGameDetailsResultBuilder,
    BoardGameGeekApiClient,
    BoardGameGeekGameInfoService,
)
from bgd.services.apis.fifth_element import (
    FifthElementApiClient,
    FifthElementSearchService,
    GameSearchResultFifthElementBuilder,
)
from bgd.services.apis.kufar import (
    GameSearchResultKufarBuilder,
    KufarApiClient,
    KufarSearchService,
)
from bgd.services.apis.national_bank import (
    NationalBankApiClient,
    NationalBankCurrencyExchangeRateBuilder,
)
from bgd.services.apis.onliner import (
    GameSearchResultOnlinerBuilder,
    OnlinerApiClient,
    OnlinerSearchService,
)
from bgd.services.apis.ozby import (
    GameSearchResultOzByBuilder,
    OzByApiClient,
    OzBySearchService,
)
from bgd.services.apis.ozon import (
    GameSearchResultOzonBuilder,
    OzonApiClient,
    OzonSearchService,
)
from bgd.services.apis.tesera import (
    TeseraApiClient,
    TeseraGameDetailsResultBuilder,
    TeseraGameInfoService,
)
from bgd.services.apis.twenty_first_vek import (
    GameSearchResultTwentyFirstVekBuilder,
    TwentyFirstVekApiClient,
    TwentyFirstVekSearchService,
)
from bgd.services.apis.vkontakte import (
    GameSearchResultVkontakteBuilder,
    VkontakteApiClient,
    VkontakteSearchService,
)
from bgd.services.apis.wildberries import (
    GameSearchResultWildberriesBuilder,
    WildberriesApiClient,
    WildberriesSearchService,
)
from bgd.services.apis.znaemigraem import (
    GameSearchResultZnaemIgraemBuilder,
    ZnaemIgraemApiClient,
    ZnaemIgraemSearchService,
)
from bgd.services.base import BaseCurrencyExchangeRateService, SimpleSuggestGameService

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
        builder=BGGGameDetailsResultBuilder,
    )

    tesera_service = providers.Singleton(
        TeseraGameInfoService,
        client=providers.Singleton(TeseraApiClient),
        builder=TeseraGameDetailsResultBuilder,
    )

    exchange_rate_service = providers.Singleton(
        BaseCurrencyExchangeRateService,
        client=providers.Singleton(NationalBankApiClient),
        base_currency=config.exchange_rate.base,
        rate_builder=NationalBankCurrencyExchangeRateBuilder,
        target_currency=config.exchange_rate.target,
    )

    kufar_search_service = providers.Singleton(
        KufarSearchService,
        client=providers.Singleton(KufarApiClient),
        game_category_id=config.kufar.game_category_id,
        result_builder=GameSearchResultKufarBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    wildberreis_search_service = providers.Singleton(
        WildberriesSearchService,
        client=providers.Singleton(WildberriesApiClient),
        game_category_id=config.wildberries.game_category_id,
        result_builder=GameSearchResultWildberriesBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    ozon_search_service = providers.Singleton(
        OzonSearchService,
        client=providers.Singleton(OzonApiClient),
        game_category_id=config.ozon.game_category_id,
        result_builder=GameSearchResultOzonBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    ozby_search_service = providers.Singleton(
        OzBySearchService,
        client=providers.Singleton(OzByApiClient),
        game_category_id=config.ozby.game_category_id,
        result_builder=GameSearchResultOzByBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    onliner_search_service = providers.Singleton(
        OnlinerSearchService,
        client=providers.Singleton(OnlinerApiClient),
        game_category_id="",
        result_builder=GameSearchResultOnlinerBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    twenty_first_vek_service = providers.Singleton(
        TwentyFirstVekSearchService,
        client=providers.Singleton(TwentyFirstVekApiClient),
        game_category_id="",
        result_builder=GameSearchResultTwentyFirstVekBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    fifth_element_service = providers.Singleton(
        FifthElementSearchService,
        client=providers.Singleton(FifthElementApiClient),
        game_category_id=config.fifthelement.game_category_id,
        result_builder=GameSearchResultFifthElementBuilder,
        search_app_id=config.fifthelement.search_app_id,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    vk_service = providers.Singleton(
        VkontakteSearchService,
        client=providers.Singleton(VkontakteApiClient),
        game_category_id="",
        group_id=config.vk.group_id,
        group_name=config.vk.group_name,
        api_token=config.vk.api_token,
        api_version=config.vk.api_version,
        limit=config.vk.limit,
        result_builder=GameSearchResultVkontakteBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )
    znaem_igraem_service = providers.Singleton(
        ZnaemIgraemSearchService,
        client=providers.Singleton(ZnaemIgraemApiClient),
        game_category_id="",
        result_builder=GameSearchResultZnaemIgraemBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    data_sources = providers.List(
        fifth_element_service,
        kufar_search_service,
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
