"""
Функции для работы с внешними API (функциональный подход).
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests
from requests.exceptions import RequestException, Timeout

from config import (
    ALPHA_VANTAGE_API_KEY,
    ALPHA_VANTAGE_URL,
    EXCHANGE_RATE_API_KEY,
    FALLBACK_CURRENCY_RATES,
    FALLBACK_STOCK_PRICES,
    FINNHUB_API_KEY,
    FINNHUB_URL,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
)

logger = logging.getLogger(__name__)

# Создаем сессию как глобальную переменную (можно было бы передавать как параметр)
_requests_session = None


def get_session():
    """Возвращает общую сессию для запросов (ленивая инициализация)."""
    global _requests_session
    if _requests_session is None:
        _requests_session = requests.Session()
        _requests_session.headers.update({"User-Agent": "BankTransactionAnalyzer/1.0"})
    return _requests_session


def make_api_request(
    url: str, params: Optional[Dict[str, Any]] = None, method: str = "GET", retries: int = MAX_RETRIES
) -> Optional[Dict[str, Any]]:
    """
    Выполняет HTTP запрос с повторными попытками.

    Args:
        url: URL для запроса
        params: Параметры запроса
        method: HTTP метод
        retries: Количество попыток

    Returns:
        Ответ в виде словаря или None при ошибке
    """
    session = get_session()

    for attempt in range(retries):
        try:
            logger.debug(f"Запрос к {url}, попытка {attempt + 1}")

            if method == "GET":
                response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            else:
                response = session.post(url, json=params, timeout=REQUEST_TIMEOUT)

            response.raise_for_status()

            # Проверяем что ответ в JSON формате
            if "application/json" in response.headers.get("Content-Type", ""):
                return response.json()
            else:
                logger.warning(f"Некорректный Content-Type: {response.headers.get('Content-Type')}")
                return None

        except Timeout as e:
            logger.warning(f"Таймаут при запросе к {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2**attempt)  # Экспоненциальная задержка
            else:
                logger.error(f"Превышено количество попыток для {url}")
                return None

        except RequestException as e:
            logger.error(f"Ошибка при запросе к {url}: {e}")
            return None

    return None


def get_currency_rates_api(currencies: List[str], base_currency: str = "RUB") -> Dict[str, float]:
    """
    Получает курсы валют через API.

    Args:
        currencies: Список валют для получения курсов
        base_currency: Базовая валюта

    Returns:
        Словарь с курсами валют
    """
    logger.info(f"💰 Получение курсов валют через API: {currencies}")

    if not EXCHANGE_RATE_API_KEY:
        logger.warning("API ключ для валют не указан, используем заглушку")
        return get_fallback_currency_rates(currencies)

    try:
        # exchangerate-api.com позволяет указывать базовую валюту
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/{base_currency}"

        data = make_api_request(url)

        if data and data.get("result") == "success":
            all_rates = data.get("conversion_rates", {})

            # Фильтруем только нужные валюты
            result = {}
            for currency in currencies:
                currency_upper = currency.upper()

                if currency_upper in all_rates:
                    result[currency] = all_rates[currency_upper]
                elif currency_upper == base_currency.upper():
                    result[currency] = 1.0  # Базовая валюта
                else:
                    logger.warning(f"Курс для валюты {currency} не найден")
                    result[currency] = 0.0

            logger.info(f"💰 Получены курсы для {len(result)} валют из API")
            return result
        else:
            logger.warning("Не удалось получить курсы валют из API, используем заглушку")
            return get_fallback_currency_rates(currencies)

    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют из API: {e}")
        return get_fallback_currency_rates(currencies)


def get_stock_prices_api(symbols: List[str]) -> Dict[str, float]:
    """
    Получает текущие цены акций через API.

    Args:
        symbols: Список символов акций

    Returns:
        Словарь с ценами акций
    """
    logger.info(f"📈 Получение цен акций через API: {symbols}")

    # Пробуем разные API по порядку
    if ALPHA_VANTAGE_API_KEY:
        prices = get_stock_prices_alpha_vantage(symbols)
        if prices:
            return prices

    if FINNHUB_API_KEY:
        prices = get_stock_prices_finnhub(symbols)
        if prices:
            return prices

    # Если оба API не сработали или нет ключей
    logger.warning("Не удалось получить цены акций из API, используем заглушку")
    return get_fallback_stock_prices(symbols)


def get_stock_prices_alpha_vantage(symbols: List[str]) -> Dict[str, float]:
    """Получает цены из Alpha Vantage."""
    try:
        prices = {}

        for symbol in symbols[:5]:  # Ограничиваем 5 запросами из-за лимитов
            params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_VANTAGE_API_KEY}

            data = make_api_request(ALPHA_VANTAGE_URL, params)

            if data and "Global Quote" in data:
                quote = data["Global Quote"]
                price_str = quote.get("05. price")
                if price_str:
                    prices[symbol] = float(price_str)

            # Задержка между запросами (Alpha Vantage имеет лимиты)
            time.sleep(1.2)  # 1.2 секунды между запросами

        if prices:
            logger.info(f"Получены цены для {len(prices)} акций из Alpha Vantage")
            return prices

    except Exception as e:
        logger.error(f"Ошибка при получении данных из Alpha Vantage: {e}")

    return {}


def get_stock_prices_finnhub(symbols: List[str]) -> Dict[str, float]:
    """Получает цены из Finnhub."""
    try:
        prices = {}

        for symbol in symbols:
            url = f"{FINNHUB_URL}/quote"
            params = {"symbol": symbol, "token": FINNHUB_API_KEY}

            data = make_api_request(url, params)

            if data and "c" in data:  # 'c' - текущая цена
                price = data.get("c")
                if price:
                    prices[symbol] = float(price)

        if prices:
            logger.info(f"Получены цены для {len(prices)} акций из Finnhub")
            return prices

    except Exception as e:
        logger.error(f"Ошибка при получении данных из Finnhub: {e}")

    return {}


def get_fallback_currency_rates(currencies: List[str]) -> Dict[str, float]:
    """Возвращает заглушечные курсы валют."""
    logger.info("Используются заглушечные курсы валют")

    result = {}
    for currency in currencies:
        currency_upper = currency.upper()
        if currency_upper in FALLBACK_CURRENCY_RATES:
            result[currency] = FALLBACK_CURRENCY_RATES[currency_upper]
        else:
            result[currency] = 0.0

    return result


def get_fallback_stock_prices(symbols: List[str]) -> Dict[str, float]:
    """Возвращает заглушечные цены акций."""
    logger.info("Используются заглушечные цены акций")

    result = {}
    for symbol in symbols:
        symbol_upper = symbol.upper()
        if symbol_upper in FALLBACK_STOCK_PRICES:
            result[symbol] = FALLBACK_STOCK_PRICES[symbol_upper]
        else:
            # Генерируем случайную цену для неизвестных акций
            import random

            result[symbol] = round(random.uniform(50, 500), 2)

    return result
