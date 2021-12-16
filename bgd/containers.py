"""
App containers
"""
import os

from dependency_injector import containers, providers
from starlette.templating import Jinja2Templates

from bgd.clients import services
from bgd.clients.builders import (
    BGGGameDetailsResultBuilder,
    GameSearchResultFifthElementBuilder,
    GameSearchResultKufarBuilder,
    GameSearchResultOnlinerBuilder,
    GameSearchResultOzByBuilder,
    GameSearchResultOzonBuilder,
    GameSearchResultTwentyFirstVekBuilder,
    GameSearchResultVkontakteBuilder,
    GameSearchResultWildberriesBuilder,
    NationalBankCurrencyExchangeRateBuilder,
    TeseraGameDetailsResultBuilder,
)
from bgd.clients.clients import (
    BoardGameGeekApiClient,
    FifthElementApiClient,
    KufarApiClient,
    NationalBankAPIClient,
    OnlinerApiClient,
    OzByApiClient,
    OzonApiClient,
    TeseraApiClient,
    TwentyFirstVekApiClient,
    VkontakteApiClient,
    WildberriesApiClient,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# pylint: disable=I1101
class ApplicationContainer(containers.DeclarativeContainer):
    """App container"""

    config = providers.Configuration()

    templates = providers.Factory(
        Jinja2Templates,
        directory=config.templates.dir,
    )

    bgg_api_client = providers.Singleton(BoardGameGeekApiClient)
    bgg_service = providers.Singleton(
        services.BoardGameGeekGameInfoService,
        client=bgg_api_client,
        builder=BGGGameDetailsResultBuilder,
    )

    tesera_api_client = providers.Singleton(TeseraApiClient)
    tesera_service = providers.Singleton(
        services.TeseraGameInfoService,
        client=tesera_api_client,
        builder=TeseraGameDetailsResultBuilder,
    )

    exchange_rate_api_client = providers.Singleton(NationalBankAPIClient)
    exchange_rate_service = providers.Singleton(
        services.CurrencyExchangeRateService,
        client=exchange_rate_api_client,
        base_currency=config.exchange_rate.base,
        rate_builder=NationalBankCurrencyExchangeRateBuilder,
        target_currency=config.exchange_rate.target,
    )

    kufar_api_client = providers.Singleton(KufarApiClient)
    kufar_search_service = providers.Singleton(
        services.KufarSearchService,
        client=kufar_api_client,
        game_category_id=config.kufar.game_category_id,
        result_builder=GameSearchResultKufarBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    wildberries_api_client = providers.Singleton(WildberriesApiClient)
    wildberreis_search_service = providers.Singleton(
        services.WildberriesSearchService,
        client=wildberries_api_client,
        game_category_id=config.wildberries.game_category_id,
        result_builder=GameSearchResultWildberriesBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    ozon_api_client = providers.Singleton(OzonApiClient)
    ozon_search_service = providers.Singleton(
        services.OzonSearchService,
        client=ozon_api_client,
        game_category_id=config.ozon.game_category_id,
        result_builder=GameSearchResultOzonBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    ozby_api_client = providers.Singleton(OzByApiClient)
    ozby_search_service = providers.Singleton(
        services.OzBySearchService,
        client=ozby_api_client,
        game_category_id=config.ozby.game_category_id,
        result_builder=GameSearchResultOzByBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    onliner_api_client = providers.Singleton(OnlinerApiClient)
    onliner_search_service = providers.Singleton(
        services.OnlinerSearchService,
        client=onliner_api_client,
        game_category_id="",
        result_builder=GameSearchResultOnlinerBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    twenty_first_vek_api_client = providers.Singleton(TwentyFirstVekApiClient)
    twenty_first_vek_service = providers.Singleton(
        services.TwentyFirstVekSearchService,
        client=twenty_first_vek_api_client,
        game_category_id="",
        result_builder=GameSearchResultTwentyFirstVekBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    fifth_element_api_client = providers.Singleton(FifthElementApiClient)
    fifth_element_service = providers.Singleton(
        services.FifthElementSearchService,
        client=fifth_element_api_client,
        game_category_id=config.fifthelement.game_category_id,
        result_builder=GameSearchResultFifthElementBuilder,
        search_app_id=config.fifthelement.search_app_id,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    vk_api_client = providers.Singleton(VkontakteApiClient)
    vk_service = providers.Singleton(
        services.VkontakteSearchService,
        client=vk_api_client,
        game_category_id="",
        group_id=config.vk.group_id,
        group_name=config.vk.group_name,
        api_token=config.vk.api_token,
        api_version=config.vk.api_version,
        limit=config.vk.limit,
        result_builder=GameSearchResultVkontakteBuilder,
        currency_exchange_rate_converter=exchange_rate_service,
    )

    data_sources = providers.List(
        kufar_search_service,
        wildberreis_search_service,
        ozon_search_service,
        ozby_search_service,
        onliner_search_service,
        twenty_first_vek_service,
        fifth_element_service,
        vk_service,
    )

    suggest_game_service = providers.Singleton(
        services.SuggestGameService,
        games=config.app.suggested_games,
    )
