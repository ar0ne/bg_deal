"""
National Bank (nb.by) API Client
"""
import datetime
import logging
from typing import Optional

from libbgg.infodict import InfoDict

from bgd.responses import Price
from bgd.services.api_clients import CurrencyExchangeRateSearcher, XmlHttpApiClient
from bgd.services.builders import CurrencyExchangeRateBuilder
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


class NationalBankCurrencyExchangeRateBuilder(CurrencyExchangeRateBuilder):
    """Builder for ExchangeRates"""

    @staticmethod
    def from_response(response: InfoDict) -> Optional[ExchangeRates]:
        """Converts response to list of exchange rates"""
        if not (response and hasattr(response, "DailyExRates")):
            return None
        currencies = response.DailyExRates.Currency
        return {
            currency.CharCode.TEXT: float(currency.Rate.TEXT) for currency in currencies
        }


class NBCurrencyExchangeRateService:
    """National bank currency exchange rate service"""

    def __init__(
        self,
        client: CurrencyExchangeRateSearcher,
        rate_builder: CurrencyExchangeRateBuilder,
        base_currency: str,
        target_currency: str,
    ) -> None:
        """
        Init exchange rate service
        :param CurrencyExchangeRateSearcher client: A searcher of currency exchange rates.
        :param CurrencyExchangeRateBuilder rate_builder: Builder for ExchangeRates model.
        :param str base_currency: 3-letters currency code from which service does conversion.
        :param str target_currency: 3-letters currency code for conversion.
        """
        self._client = client
        self._builder = rate_builder
        self._target_currency = target_currency
        self._base_currency = base_currency
        self._rates: Optional[ExchangeRates] = None
        self._expiration_date: Optional[datetime.date] = None

    async def convert(self, price: Optional[Price]) -> Optional[Price]:
        """Convert amount to another currency"""
        if not price:
            return None
        rates = await self.get_rates()
        if not (rates and self._target_currency in rates):
            return None
        exchange_rate = rates[self._target_currency]
        return Price(
            amount=round(price.amount / exchange_rate),
            currency=self._target_currency,
        )

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
            self._rates = self._builder.from_response(resp.response)
            self._expiration_date = today + datetime.timedelta(days=1)
        return self._rates
