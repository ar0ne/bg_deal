"""
Exchange Rate service
"""
import datetime
from typing import Optional

from fastapi_cache.decorator import cache

from bgd.constants import BYN, USD
from bgd.responses import Price
from bgd.services.abc import CurrencyExchangeRateResultBuilder
from bgd.services.api_clients import CurrencyExchangeRateSearcher
from bgd.services.types import ExchangeRates


class CurrencyExchangeRateService:
    """National bank currency exchange rate service"""

    def __init__(
        self,
        client: CurrencyExchangeRateSearcher,
        result_builder: CurrencyExchangeRateResultBuilder,
    ) -> None:
        """
        Init exchange rate service
        :param CurrencyExchangeRateSearcher client: A searcher of currency exchange rates.
        """
        self._client = client
        self._rates: Optional[ExchangeRates] = None
        self._expiration_date: Optional[datetime.date] = None
        self._result_builder = result_builder

    async def convert(self, price: Optional[Price], target_currency: str = USD) -> Optional[Price]:
        """Convert amount to another currency"""
        if not price:
            return None
        if price.currency == target_currency:
            return None
        rates = await self.get_rates()
        if not rates:
            return None
        # rates = {"USD": 2.95, "RUB": 0.039, ...}
        if price.currency == BYN and target_currency not in rates:
            return None
        target = target_currency
        if price.currency != BYN:
            # rates could be only for base BYN, reverse conversion
            target = price.currency
        exchange_rate = rates[target]
        return Price(
            amount=self._calculate_amount(price, target_currency, exchange_rate),
            currency=target_currency,
        )

    def _calculate_amount(self, price: Price, target_currency: str, exchange_rate: float) -> int:
        """
        Сalculate amount for targe currency.

        >>> _calculate_amount(Price(amount=1000, currency="RUB"), "BYN", 0.0399)
        39
        >>> _calculate_amount(Price(amount=10, currency="BYN"), "USD", 2.5043)
        4
        """
        if target_currency != BYN:
            return round(price.amount / exchange_rate)
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
            if not (resp and resp.response):
                return None
            self._rates = self._result_builder.build(resp.response)
            self._expiration_date = today + datetime.timedelta(days=1)
        return self._rates
