"""
National Bank (nb.by) API Client
"""
import datetime
import logging
from typing import Optional

from libbgg.infodict import InfoDict

from bgd.services.api_clients import XmlHttpApiClient
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
        :param: date on_date: Date for which we need currency exchange rates.
        """
        formatted_date = on_date.strftime("%m/%d/%Y")
        log.info("Getting currency exchange rates for %s", formatted_date)
        path = f"{self.EXCHANGE_RATE_PATH}?ondate={formatted_date}"
        return await self.connect(GET, self.BASE_URL, path)


class NationalBankCurrencyExchangeRateResultBuilder:
    """Builder for ExchangeRates"""

    @staticmethod
    def create(response: InfoDict) -> Optional[ExchangeRates]:
        """Converts response to list of exchange rates"""
        if not (response and hasattr(response, "DailyExRates")):
            return None
        currencies = response.DailyExRates.Currency
        return {currency.CharCode.TEXT: float(currency.Rate.TEXT) for currency in currencies}
