"""
API Client for Belarusian Currency and Stock Exchange (BCSE)
"""
import datetime
import logging
from typing import Optional

from bgd.services.api_clients import JsonHttpApiClient
from bgd.services.constants import GET
from bgd.services.responses import APIResponse
from bgd.services.types import ExchangeRates

log = logging.getLogger(__name__)


class BCSEExchangepiClient(JsonHttpApiClient):
    """API client for getting exchange rates on date from BCSE"""

    BASE_URL = "https://www.bcse.by"
    EXCHANGE_RATE_PATH = "/CurrencyMarket/GetNBRBCurrency"

    async def get_currency_exchange_rates(self, on_date: datetime.date) -> APIResponse:
        """
        Get currency exchange rates at date.
        :param: date on_date: Date for which we need currency exchange rates.
        """
        formatted_date = on_date.strftime("%m/%d/%Y")
        log.info("Getting currency exchange rates for %s", formatted_date)
        path = f"{self.EXCHANGE_RATE_PATH}?sDate={formatted_date}"
        return await self.connect(GET, self.BASE_URL, path)


class BCSECurrencyExchangeRateResultBuilder:
    """Builder for ExchangeRates"""

    @staticmethod
    def build(response: dict) -> Optional[ExchangeRates]:
        """Converts response to list of exchange rates"""
        if not (response and hasattr(response, "rates")):
            return None
        rates = response["rates"]
        return {rate["value"]: rate["number"] for rate in rates}
