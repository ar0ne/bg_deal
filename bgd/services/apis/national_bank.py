"""
National Bank (nb.by) API Client
"""
import datetime
import logging
from typing import Optional

from fastapi_cache.decorator import cache
from libbgg.infodict import InfoDict

from bgd.constants import BYN, RUB, USD
from bgd.responses import Price
from bgd.services.abc import CurrencyExchangeRateFactory
from bgd.services.api_clients import CurrencyExchangeRateSearcher, XmlHttpApiClient
from bgd.services.constants import GET
from bgd.services.responses import APIResponse
from bgd.services.types import ExchangeRates

log = logging.getLogger(__name__)


class NationalBankApiClient(XmlHttpApiClient):
    """API client for Belarus national bank"""

    BASE_URL = "https://www.nbrb.by"
    EXCHANGE_RATE_PATH = "/services/xmlexrates.aspx"

    async def get_currency_exchange_rates(self, on_date: datetime.date) -> APIResponse:
        """
        Get currency exchange rates at date.
        :param date on_date: Date for which we need currency exchange rates.
        """
        formatted_date = on_date.strftime("%m/%d/%Y")
        log.info("Getting currency exchange rates for %s", formatted_date)
        url = f"{self.EXCHANGE_RATE_PATH}?ondate={formatted_date}"
        return await self.connect(GET, self.BASE_URL, url)


class NationalBankCurrencyExchangeRateFactory:
    """Builder for ExchangeRates"""

    @staticmethod
    def create(response: InfoDict) -> Optional[ExchangeRates]:
        """Converts response to list of exchange rates"""
        if not (response and hasattr(response, "DailyExRates")):
            return None
        currencies = response.DailyExRates.Currency
        return {currency.CharCode.TEXT: float(currency.Rate.TEXT) for currency in currencies}


class NationalBankCurrencyExchangeRateService:
    """National bank currency exchange rate service"""

    def __init__(self, client: CurrencyExchangeRateSearcher) -> None:
        """
        Init exchange rate service
        :param CurrencyExchangeRateSearcher client: A searcher of currency exchange rates.
        """
        self._client = client
        self._rates: Optional[ExchangeRates] = None
        self._expiration_date: Optional[datetime.date] = None

    async def convert(self, price: Optional[Price], target_currency: str = USD) -> Optional[Price]:
        """Convert amount to another currency"""
        if not price:
            return None
        if price.currency == target_currency:
            return None
        rates = await self.get_rates()
        if not rates:
            return None
        if price.currency == BYN and target_currency not in rates:
            return None
        target = target_currency
        if price.currency != BYN:
            # nb providers rates only for BYN, reverse conversion otherwise
            target = price.currency
        exchange_rate = rates[target]
        return Price(
            amount=self._calculate_amount(price, target_currency, exchange_rate),
            currency=target_currency,
        )

    def _calculate_amount(self, price: Price, target_currency: str, exchange_rate: float) -> int:
        """calculate amount"""
        if target_currency != BYN:
            return round(price.amount / exchange_rate)
        if price.currency == RUB:
            return round(price.amount / 100 * exchange_rate)
        return round(price.amount * exchange_rate)

    @cache()
    async def get_rates(self) -> Optional[ExchangeRates]:
        """Get actual currency exchange rates"""
        today = datetime.date.today()
        if self._expiration_date and self._expiration_date <= today:
            self._rates = None
            self._expiration_date = None
        if not self._rates:
            # for safety let's use yesterday rates
            yesterday = today - datetime.timedelta(days=1)
            resp = await self._client.get_currency_exchange_rates(yesterday)
            self._rates = self.result_factory.create(resp.response)
            self._expiration_date = today + datetime.timedelta(days=1)
        return self._rates

    @property
    def result_factory(self) -> CurrencyExchangeRateFactory:
        """Create result factory"""
        return NationalBankCurrencyExchangeRateFactory()
