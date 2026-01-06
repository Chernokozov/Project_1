"""
Тесты для views.py
"""

import os
import sys

import pandas as pd

from src.views import events_page, home_page_real

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))


def test_home_page_real_basic() -> None:
    """
    Базовый тест главной страницы.
    """
    data = {
        "Дата операции": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "Сумма операции": [-1500, -800, 50000],
        "Категория": ["Супермаркеты", "Рестораны", "Зарплата"],
        "Описание": ["Пятерочка", "Starbucks", "Зарплата"],
        "Номер карты": ["****1234", "****1234", "****5678"],
    }
    df = pd.DataFrame(data)

    result = home_page_real("2024-01-15 14:30:00", df)

    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert len(result["cards"]) == 2
    assert result["greeting"] == "Добрый день"


def test_home_page_real_empty_data() -> None:
    """
    Тест с пустыми данными.
    """
    df = pd.DataFrame()
    result = home_page_real("2023-01-15 08:30:00", df)

    assert result["greeting"] == "Доброе утро"
    assert len(result["cards"]) == 0
    assert len(result["top_transactions"]) == 0


def test_event_page_month() -> None:
    """Тест страницы событий за месяц."""
    result = events_page("2024-01-15 14:30:00", "M")

    assert "period" in result
    assert "expenses" in result
    assert "income" in result
    assert "currencies" in result
    assert "stocks" in result

    assert result["period"]["type"] == "M"

    assert isinstance(result["expenses"]["total"], float)
    assert isinstance(result["income"]["total"], float)


def test_events_page_week() -> None:
    """Тест страницы события за неделю."""
    result = events_page("2024-01-15 12:30:00", "W")
    assert result["period"]["type"] == "W"


def test_events_page_year() -> None:
    """Тест страницы событий за год."""
    result = events_page("2024-01-15 14:30:00", "Y")
    assert result["period"]["type"] == "Y"
