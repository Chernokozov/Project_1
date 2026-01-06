"""
Функции для веб-страниц.
"""

import logging
from datetime import datetime
from typing import Any, Dict

import pandas as pd

from src.config import DATA_DIR
from src.utils import get_currency_rates, get_greeting, get_stock_prices, load_transactions, load_user_settings

logger = logging.getLogger(__name__)


def home_page_real(date_time_str: str, df) -> Dict[str, Any]:
    """
    Реальная функция главной страницы с реальными данными.
    """

    logger.info(f"📄 Генерация главной страницы для {date_time_str}")

    # 1. Приветствие
    greeting = get_greeting(date_time_str.split(" ")[1] if " " in date_time_str else "12:00:00")

    # 2. Анализ по картам
    cards_analysis = []
    if "Номер карты" in df.columns:
        # Группируем по картам
        for card in df["Номер карты"].unique():
            card_data = df[df["Номер карты"] == card]

            # Сумма расходов (отрицательные значения)
            expenses = card_data[card_data["Сумма операции"] < 0]
            total_spent = abs(expenses["Сумма операции"].sum())

            # Кешбэк: 1 рубль на каждые 100 рублей
            cashback = int(total_spent // 100)

            cards_analysis.append(
                {
                    "last_digits": str(card)[-4:] if len(str(card)) >= 4 else str(card),
                    "total_spent": round(total_spent, 2),
                    "cashback": cashback,
                }
            )

    # 3. Топ-5 транзакций по сумме (самые крупные расходы)
    top_transactions = []
    if len(df) > 0:
        # Берем топ по модулю суммы (самые большие траты)
        df_sorted = df.copy()
        df_sorted["abs_amount"] = df_sorted["Сумма операции"].abs()
        top_df = df_sorted.nlargest(5, "abs_amount")

        top_transactions = [
            {
                "description": str(row.get("Описание", "Без описания")),
                "amount": float(row["Сумма операции"]),
                "date": str(row.get("Дата операции", ""))[:10] if pd.notnull(row.get("Дата операции")) else "",
                "category": str(row.get("Категория", "")),
            }
            for _, row in top_df.iterrows()
        ]

    # 4. Курсы валют (заглушка - позже заменим на API)
    currencies = {"USD": 90.5, "EUR": 99.2, "GBP": 115.0}

    # 5. Цены акций (заглушка)
    stocks = {"AAPL": 185.30, "GOOGL": 145.20, "MSFT": 375.50, "TSLA": 250.75}

    # 6. Форматируем период (исправляем ошибку с Timestamp)
    if len(df) > 0 and "Дата операции" in df.columns:
        # Преобразуем даты в строки
        min_date = df["Дата операции"].min()
        max_date = df["Дата операции"].max()

        # Проверяем, что это объекты даты
        if hasattr(min_date, "strftime"):
            period_str = f"{min_date.strftime('%Y-%m-%d')} - {max_date.strftime('%Y-%m-%d')}"
        else:
            period_str = f"{str(min_date)[:10]} - {str(max_date)[:10]}"
    else:
        period_str = "N/A - N/A"

    result = {
        "greeting": greeting,
        "cards": cards_analysis,
        "top_transactions": top_transactions,
        "currencies": currencies,
        "stocks": stocks,
        "summary": {"total_transactions": len(df), "period": period_str},
    }

    logger.info(f"Сгенерирована главная страница: {len(cards_analysis)} карт, {len(top_transactions)} топ-транзакций")
    return result


def events_page(date_time_str: str, period: str = "M") -> Dict[str, Any]:
    """
    Генерирует данные для страницы "События".
    """

    logger.info(f"📊 Генерация страницы 'События' для {date_time_str}, период: {period}")

    df = load_transactions(DATA_DIR)

    # Парсим дату
    try:
        if " " in date_time_str:
            analysis_date = pd.to_datetime(date_time_str.split(" ")[0])
        else:
            analysis_date = pd.to_datetime(date_time_str)
    except Exception as e:
        logger.info(f"Неудалось обнаружить дату {e}")
        analysis_date = datetime.now()

    # Определяем период
    analysis_date_ts = pd.Timestamp(analysis_date)

    if period == "W":
        # Начало недели (понедельник)
        start_date = analysis_date_ts - pd.Timedelta(days=analysis_date_ts.weekday())
        end_date = start_date + pd.Timedelta(days=6)
    elif period == "M":
        start_date = analysis_date_ts.replace(day=1)
        next_month = start_date + pd.Timedelta(days=32)
        end_date = next_month.replace(day=1) - pd.Timedelta(days=1)
    elif period == "Y":
        start_date = analysis_date_ts.replace(month=1, day=1)
        end_date = analysis_date_ts.replace(month=12, day=31)
    elif period == "ALL":
        start_date = df["Дата операции"].min()
        end_date = df["Дата операции"].max()
    else:
        start_date = analysis_date_ts.replace(day=1)
        next_month = start_date + pd.Timedelta(days=32)
        end_date = next_month.replace(day=1) - pd.Timedelta(days=1)

    # Фильтруем данные по периоду
    mask = (df["Дата операции"] >= pd.Timestamp(start_date)) & (df["Дата операции"] <= pd.Timestamp(end_date))
    period_df = df.loc[mask].copy()

    # 1. Анализ расходов
    expenses_df = period_df[period_df["Сумма операции"] < 0].copy()
    total_expenses = abs(expenses_df["Сумма операции"].sum())

    # Группируем расходы по категориям - ИСПРАВЛЕНИЕ: преобразуем в числа
    expenses_by_category = expenses_df.groupby("Категория")["Сумма операции"].sum().abs()
    expenses_by_category = expenses_by_category.sort_values(ascending=False)

    # Берем топ-7 категорий, остальные в "Остальное"
    if len(expenses_by_category) > 7:
        top_expenses = expenses_by_category.head(7)
        other_expenses = expenses_by_category[7:].sum()

        # Преобразуем в обычный словарь с числами
        expenses_dict = {}
        for category, amount in top_expenses.items():
            expenses_dict[str(category)] = float(amount)
        expenses_dict["Остальное"] = float(other_expenses)
    else:
        expenses_dict = {str(k): float(v) for k, v in expenses_by_category.items()}

    # Переводы и наличные - ИСПРАВЛЕНИЕ: извлекаем правильно
    transfers_cash = {}
    for category in ["Переводы", "Наличные"]:
        if category in expenses_dict:
            transfers_cash[category] = expenses_dict.pop(category)

    # 2. Анализ поступлений
    income_df = period_df[period_df["Сумма операции"] > 0].copy()
    total_income = income_df["Сумма операции"].sum()

    income_by_category = income_df.groupby("Категория")["Сумма операции"].sum()
    income_by_category = income_by_category.sort_values(ascending=False)

    # Преобразуем в словарь с числами
    income_dict = {str(k): float(v) for k, v in income_by_category.items()}

    # 3. Курсы валют и акции
    settings = load_user_settings()
    currencies = get_currency_rates(settings.get("user_currencies", ["USD", "EUR"]))
    stocks = get_stock_prices(settings.get("user_stocks", ["AAPL", "GOOGL"]))

    # Формируем результат с округлением
    result = {
        "period": {"type": period, "start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")},
        "expenses": {
            "total": round(float(total_expenses), 2),
            "main_categories": {k: round(v, 2) for k, v in expenses_dict.items()},
            "transfers_cash": {k: round(v, 2) for k, v in transfers_cash.items()},
        },
        "income": {
            "total": round(float(total_income), 2),
            "main_categories": {k: round(v, 2) for k, v in income_dict.items()},
        },
        "currencies": currencies,
        "stocks": stocks,
        "summary": {"total_transactions": len(period_df), "balance": round(float(total_income - total_expenses), 2)},
    }

    logger.info(f"Сгенерирована страница 'События': {len(period_df)} транзакций")
    return result
