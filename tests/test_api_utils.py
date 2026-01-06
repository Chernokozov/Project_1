"""
Тесты для API утилит (функциональный подход).
"""

import sys
from pathlib import Path
from unittest.mock import patch

from src.api_utils import (
    get_currency_rates_api,
    get_fallback_currency_rates,
    get_fallback_stock_prices,
    get_stock_prices_api,
)

sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))


def test_get_fallback_currency_rates() -> None:
    """Тест получения заглушечных курсов валют."""
    currencies = ["USD", "EUR", "GBP", "UNKNOWN"]
    rates = get_fallback_currency_rates(currencies)

    assert isinstance(rates, dict)
    assert "USD" in rates
    assert "EUR" in rates
    assert rates["UNKNOWN"] == 0.0
    assert isinstance(rates["USD"], float)


def test_get_fallback_stock_prices() -> None:
    """Тест получения заглушечных цен акций."""
    symbols = ["AAPL", "GOOGL", "UNKNOWN"]
    prices = get_fallback_stock_prices(symbols)

    assert isinstance(prices, dict)
    assert "AAPL" in prices
    assert "GOOGL" in prices
    assert "UNKNOWN" in prices
    assert isinstance(prices["AAPL"], float)


@patch("api_utils.make_api_request")
def test_get_currency_rates_api_success(mock_request):
    """Тест успешного получения курсов валют из API."""
    mock_data = {"result": "success", "conversion_rates": {"USD": 0.011, "EUR": 0.010, "GBP": 0.0085}}
    mock_request.return_value = mock_data

    currencies = ["USD", "EUR"]
    rates = get_currency_rates_api(currencies)

    assert isinstance(rates, dict)
    assert "USD" in rates
    assert rates["USD"] == 0.011


@patch("api_utils.make_api_request")
def test_get_currency_rates_api_failure(mock_request):
    """Тест получения курсов при ошибке API."""
    mock_request.return_value = None

    currencies = ["USD", "EUR"]
    rates = get_currency_rates_api(currencies)

    # Должны вернуться заглушечные курсы
    assert isinstance(rates, dict)
    assert "USD" in rates


@patch("api_utils.get_stock_prices_alpha_vantage")
def test_get_stock_prices_api_with_alpha_vantage(mock_alpha):
    """Тест получения цен через Alpha Vantage."""
    mock_alpha.return_value = {"AAPL": 185.30, "GOOGL": 145.20}

    with patch("api_utils.ALPHA_VANTAGE_API_KEY", "test_key"):
        prices = get_stock_prices_api(["AAPL", "GOOGL"])

    assert isinstance(prices, dict)
    assert prices["AAPL"] == 185.30
    assert prices["GOOGL"] == 145.20


def test_get_stock_prices_api_fallback() -> None:
    """Тест получения заглушечных цен при отсутствии API ключей."""
    with patch("api_utils.ALPHA_VANTAGE_API_KEY", ""), patch("api_utils.FINNHUB_API_KEY", ""):
        prices = get_stock_prices_api(["AAPL", "GOOGL"])

    # Должны вернуться заглушечные цены
    assert isinstance(prices, dict)
    assert "AAPL" in prices
    assert isinstance(prices["AAPL"], float)
