"""
Тесты для сервисов
"""

import os
import sys

from src.services import (
    find_personal_transfers,
    find_phone_numbers,
    investment_bank,
    profitable_cashback_categories,
    simple_search,
)
from src.utils import get_currency_rates

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))


def test_simple_search_finds_by_description() -> None:
    """
    Тест: поиск находит по описанию.
    """
    transactions = [{"Описание": "Пятерочка", "Категория": "Магазин"}, {"Описание": "Starbucks", "Категория": "Кафе"}]

    result = simple_search("пятер", transactions)

    assert len(result) == 1
    assert result[0]["Описание"] == "Пятерочка"


def test_simple_search_finds_by_category() -> None:
    """Тест: находит по категории."""
    transactions = [{"Описание": "Покупка", "Категория": "Супермаркет"}, {"Описание": "Обед", "Категория": "Ресторан"}]
    result = simple_search("супермаркет", transactions)

    assert len(result) == 1
    assert result[0]["Категория"] == "Супермаркет"


def test_simple_search_empty_query() -> None:
    """Тест: пустой запрос возвращает пустой список."""
    transactions = [{"Описание": "Пятерочка", "Категория": "Магазин"}]
    result = simple_search("", transactions)
    assert result == []


def test_simple_search_no_results() -> None:
    """Тест: если ничего не найдено, возвращает пустой список."""
    transactions = [{"Описание": "Пятерочка", "Категория": "Магазин"}]
    result = simple_search("несуществующее", transactions)
    assert result == []


def test_profitable_cashback_categories() -> None:
    """Тест анализа выгодных категорий."""
    transactions = [
        {
            "Дата операции": "2024-01-15",
            "Сумма операции": -1500.0,
            "Категория": "Супермаркеты",
            "Описание": "Пятерочка",
        },
        {"Дата операции": "2024-01-16", "Сумма операции": -800.0, "Категория": "Рестораны", "Описание": "Starbucks"},
        {"Дата операции": "2024-01-17", "Сумма операции": -2000.0, "Категория": "Супермаркеты", "Описание": "Магнит"},
        {
            "Дата операции": "2024-02-01",  # Другой месяц - не должен учитываться
            "Сумма операции": -1000.0,
            "Категория": "Транспорт",
            "Описание": "Такси",
        },
    ]
    result = profitable_cashback_categories(2024, 1, transactions)
    assert "Супермаркеты" in result
    assert "Рестораны" in result
    assert "Транспорт" not in result
    assert result["Супермаркеты"] == 35.0
    assert result["Рестораны"] == 8.0


def test_investment_bank_basic() -> None:
    """Базовый тест Инвесткопилки."""
    # Тестовые данные
    transactions = [
        {
            "Дата операции": "2024-01-15",
            "Сумма операции": -1712.0,  # Покупка
            "Категория": "Супермаркеты",
            "Описание": "Пятерочка",
        },
        {
            "Дата операции": "2024-01-16",
            "Сумма операции": -849.0,  # Еще покупка
            "Категория": "Рестораны",
            "Описание": "Starbucks",
        },
        {
            "Дата операции": "2024-01-17",
            "Сумма операции": 5000.0,  # Поступление - не должно учитываться
            "Категория": "Зарплата",
            "Описание": "Зарплата",
        },
        {
            "Дата операции": "2024-02-01",  # Другой месяц - не должен учитываться
            "Сумма операции": -1000.0,
            "Категория": "Транспорт",
            "Описание": "Такси",
        },
    ]

    # Тест 1: округление до 50 рублей
    result = investment_bank("2024-01", transactions, 50)

    # Проверяем расчет:
    # 1) 1712 округляется вверх: 1712/50=34.24 → ceil=35 → 35*50=1750 → разница 38
    # 2) 849 округляется: 849/50=16.98 → ceil=17 → 17*50=850 → разница 1
    # Итого: 39 рублей
    expected_result = 39.0
    assert abs(result - expected_result) < 0.01, f"Ожидалось {expected_result}, получено {result}"
    print(f"✅ Тест 1 пройден: {result} == {expected_result}")

    # Тест 2: округление до 100 рублей
    result = investment_bank("2024-01", transactions, 100)
    # 1712 → 1800 (88), 849 → 900 (51), итого 139
    assert result == 139.0, f"Ожидалось 139.0, получено {result}"
    print(f"✅ Тест 2 пройден: {result} == 139.0")

    # Тест 3: другой месяц (ФЕВРАЛЬ 2024)
    result = investment_bank("2024-02", transactions, 50)
    # Только 1000 → 1050 (50)
    assert result == 00.0, f"Ожидалось 00.0, получено {result}"
    print(f"✅ Тест 3 пройден: {result} == 00.0")


def test_investment_bank_edge_cases() -> None:
    """Тест крайних случаев"""
    assert investment_bank("2024-04", [], 50) == 0.0
    transactions = [{"Дата операции": "2024-01-15", "Сумма операции": 5000.0}]
    assert investment_bank("2024-01", transactions, 50) == 0.0
    transactions = [{"Дата операции": "2024-01-15", "Сумма операции": -100.0}]
    assert investment_bank("2024-01", transactions, 999) == 0.0  # 100 → 100 (0)


def test_find_personal_transfers() -> None:
    """Тест поиска переводов физлицам."""

    transactions = [
        {"Категория": "Переводы", "Описание": "Перевод Валерий А. за обед", "Сумма операции": -1000},
        {"Категория": "Переводы", "Описание": "Сергей З. на день рождения", "Сумма операции": -2000},
        {"Категория": "Переводы", "Описание": "Анна М. за подарок", "Сумма операции": -1500},  # Добавляем еще один
        {"Категория": "Супермаркеты", "Описание": "Магнит", "Сумма операции": -1500},  # Не перевод
        {
            "Категория": "Переводы",  # Перевод, но не физлицо (нет Имя Ф.)
            "Описание": "Оплата услуг",
            "Сумма операции": -500,
        },
    ]

    results = find_personal_transfers(transactions)

    # Должно найти 3 перевода физлицам
    assert len(results) == 3

    # Проверяем что нашли правильные
    descriptions = [r["Описание"] for r in results]
    assert any("Валерий" in desc for desc in descriptions)
    assert any("Сергей" in desc for desc in descriptions)
    assert any("Анна" in desc for desc in descriptions)


def test_get_currency_rates() -> None:
    """Тест получения курсов валют."""
    currencies = ["USD", "EUR", "GBP"]
    rates = get_currency_rates(currencies)

    assert len(rates) == 3
    assert "USD" in rates
    assert "EUR" in rates
    assert "GBP" in rates
    assert isinstance(rates["USD"], float)


def test_find_phone_numbers() -> None:
    """Тест поиска телефонных номеров."""
    transactions = [
        {"Описание": "Пополнение телефона +7 921 111-22-33"},
        {"Описание": "МТС Mobile +7 981 333-44-55"},
        {"Описание": "Я МТС 8 921 11-22-33"},
        {"Описание": "Простая покупка без номера"},
        {"Описание": "Тинькофф Мобайл +7 995 555-55-55"},
    ]

    results = find_phone_numbers(transactions)
    assert len(results) == 4
    descriptions = [r["Описание"] for r in results]
    assert any("+7 921 111-22-33" in desc for desc in descriptions)
    assert any("+7 995 555-55-55" in desc for desc in descriptions)
