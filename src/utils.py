"""
Утилиты для работы с данными
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.config import FALLBACK_CURRENCY_RATES, FALLBACK_STOCK_PRICES
from src.api_utils import get_currency_rates_api, get_stock_prices_api
from src.file_utils import get_data_dir, load_json_file

logger = logging.getLogger(__name__)


def read_excel_file(filepath: str) -> pd.DataFrame:
    """
    Читает Excel-файл с транзакциями.
    """
    try:
        path = Path(filepath) if isinstance(filepath, str) else filepath
        logger.info(f"Чтение файла {path}")

        df = pd.read_excel(path)
        logger.info(f"Успешно прочитано {len(df)} строк")
        return df

    except FileNotFoundError as e:
        logger.error(f"Файл не найден: {filepath} {e}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        raise ValueError(f"Ошибка чтения файла {filepath}: {e}")


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает пользовательские настройки.

    Returns:
        Словарь с настройками или значения по умолчанию
    """
    settings_path = get_data_dir().parent / "user_settings.json"

    settings = load_json_file(settings_path)

    if not settings:
        logger.warning("Файл user_settings.json не найден или пуст, используются настройки по умолчанию")
        settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}

    logger.info("Пользовательские настройки загружены")
    return settings


def get_greeting(time_str: str) -> str:
    """
    Определяет приветствие по времени суток.
    """
    try:
        if " " in time_str:
            time_part = time_str.split(" ")[1]
        else:
            time_part = time_str

        time_obj = datetime.strptime(time_part, "%H:%M:%S").time()

        if time_obj.hour < 6:
            return "Доброй ночи"
        elif time_obj.hour < 12:
            return "Доброе утро"
        elif time_obj.hour < 18:
            return "Добрый день"
        elif time_obj.hour < 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"

    except ValueError as e:
        logger.error(f"Некорректный формат времени: {time_str}. Ошибка: {e}")
        return "Здравствуйте"


def create_sample_data() -> pd.DataFrame:
    """
    Создает тестовые данные для разработкию
    Это временная функция
    """
    data = {
        "Дата операции": ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18"],
        "Сумма операции": [-1500.50, -800.00, 5000.00, -200.75],
        "Категория": ["Супермаркеты", "Рестораны", "Зарплата", "Транспорт"],
        "Описание": ["Пятерочка", "Starbucks", "Зарплата Январь", "Такси домой"],
        "Номер карты": ["****1234", "****1234", "****5678", "****5678"],
        "Статус": ["OK", "OK", "OK", "OK"],
        "Кешбэк": [15.00, 8.00, 0, 2.00],
    }

    return pd.DataFrame(data)


def parse_date_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Парсит колонку с датами в DataFrame.

    Args:
        df: DataFrame с данными
        column_name: Имя колонки с датами

    Returns:
        DataFrame с распарсенными датами
    """
    if column_name not in df.columns:
        logger.warning(f"Колонка '{column_name}' не найдена в DataFrame")
        return df

    try:
        # Пробуем русский формат (день.месяц.год)
        df[column_name] = pd.to_datetime(df[column_name], format="%d.%m.%Y %H:%M:%S", dayfirst=True, errors="coerce")
        logger.info(f"Даты в колонке '{column_name}' распознаны в формате ДД.ММ.ГГГГ ЧЧ:ММ:СС")

    except (ValueError, TypeError):
        try:
            # Пробуем стандартный парсинг с dayfirst=True
            df[column_name] = pd.to_datetime(df[column_name], dayfirst=True, errors="coerce")
            logger.info(f"Даты в колонке '{column_name}' распознаны с dayfirst=True")

        except (ValueError, TypeError) as e:
            logger.warning(f"Не удалось распознать даты в колонке '{column_name}': {e}")

    return df


def load_transactions(filepath: str) -> pd.DataFrame:
    """
    Загружает транзакции с правильным парсингом дат.

    Args:
        filepath: Путь к файлу (по умолчанию data/operations.xlsx)

    Returns:
        DataFrame с транзакциями
    """
    if filepath is None:
        filepath = get_data_dir() / "operations.xlsx"

    try:
        df = read_excel_file(filepath)

        # Парсим даты в нужных колонках
        date_columns = ["Дата операции", "Дата платежа"]
        for col in date_columns:
            df = parse_date_column(df, col)

        # Сортируем по дате (новые сверху)
        if "Дата операции" in df.columns:
            df = df.sort_values("Дата операции", ascending=False)

        return df

    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return create_sample_data()
    except Exception as e:
        logger.error(f"Неожиданная ошибка при загрузке данных: {e}")
        return create_sample_data()


def get_currency_rates(currencies: List[str]) -> Dict[str, float]:
    """
    Получает курсы валют (обертка над API функцией).

    Args:
        currencies: Список валют для получения курсов

    Returns:
        Словарь с курсами валют
    """
    logger.info(f"💰 Получение курсов валют: {currencies}")

    try:
        return get_currency_rates_api(currencies)

    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        # Возвращаем заглушку при ошибке
        return {
            curr: FALLBACK_CURRENCY_RATES.get(curr.upper(), 0.0)
            for curr in currencies
            if curr.upper() in FALLBACK_CURRENCY_RATES
        }


def get_stock_prices(stocks: List[str]) -> Dict[str, float]:
    """
    Получает цены акций (обертка над API функцией).

    Args:
        stocks: Список акций для получения цен

    Returns:
        Словарь с ценами акций
    """
    logger.info(f"📈 Получение цен акций: {stocks}")

    try:
        return get_stock_prices_api(stocks)

    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {e}")
        # Возвращаем заглушку при ошибке
        return {
            stock: FALLBACK_STOCK_PRICES.get(stock.upper(), 100.0)
            for stock in stocks
            if stock.upper() in FALLBACK_STOCK_PRICES
        }
