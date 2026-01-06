import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))


@pytest.fixture
def sample_dataframe():
    """
    Фикстура с тестовым DataFrame.
    """
    data = {
        "Дата операции": ["2024-01-01", "2024-01-02"],
        "Сумма операции": [1000, 2000],
        "Категория": ["Еда", "Транспорт"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми транзакциями."""
    return [
        {
            "Дата операции": "2024-01-15",
            "Описание": "Покупка в супермаркете",
            "Категория": "Супермаркеты",
            "Сумма операции": -1500.50,
        },
        {
            "Дата операции": "2024-01-02",
            "Описание": "Обед в кафе Starbucks",
            "Категория": "Рестораны",
            "Сумма операции": -800.00,
        },
    ]


@pytest.fixture
def create_test_dataframe():
    """Фикстура для создания тестового DanaFrame."""

    def _create_test_dataframe(days=90):
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in range(days)]

        data = {
            "Дата операции": dates,
            "Сумма операции": [-1000.0] * days,  # Все траты по 1000
            "Категория": ["Тест"] * days,
        }
        return pd.DataFrame(data)

    return _create_test_dataframe
