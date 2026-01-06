"""
Сервисы для анализа транзакций.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def simple_search(query: str, transactions: List[Dict]) -> List[Dict]:
    """
    Ищет транзакции по ключевому слову.
    :param query:
    :param transactions:
    :return:
    """
    logger.info(f"Ищем: {query}")
    if not query:
        return []

    query = query.lower().strip()
    results = []

    for transaction in transactions:
        description = str(transaction.get("Описание", "")).lower()
        category = str(transaction.get("Категория", "")).lower()
        if query in description or query in category:
            results.append(transaction)

    logger.info(f"Найдено: {len(results)} транзакций")
    return results


def profitable_cashback_categories(year: int, month: int, transactions: List[Dict]) -> Dict[str, float]:
    """
    Анализирует, сколько можно заработать кешбэка в каждой категории.
    Работает с разными форматами дат.
    """
    logger.info(f"💰 Анализ выгодных категорий для {month}.{year}")

    # Фильтруем транзакции по году и месяцу
    filtered_transactions = []
    for transaction in transactions:
        try:
            trans_date = str(transaction.get("Дата операции", ""))

            if not trans_date:
                continue

            # Пробуем разные форматы дат
            # Формат 1: "2024-01-15"
            # Формат 2: "15.01.2024"
            # Формат 3: "2024-01-15 14:30:00"

            trans_year = None
            trans_month = None

            # Проверяем формат с точками (ДД.ММ.ГГГГ)
            if "." in trans_date and len(trans_date) >= 10:
                parts = trans_date.split(".")
                if len(parts) >= 3:
                    try:
                        trans_year = int(parts[2][:4])  # Берем первые 4 цифры года
                        trans_month = int(parts[1])
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Ошибка парсинга даты {trans_date}: {e}")
                        continue

            # Проверяем формат с дефисами (ГГГГ-ММ-ДД)
            elif "-" in trans_date and len(trans_date) >= 10:
                parts = trans_date.split("-")
                if len(parts) >= 2:
                    try:
                        trans_year = int(parts[0])
                        trans_month = int(parts[1])
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Ошибка парсинга даты {trans_date}: {e}")
                        continue

            # Если нашли год и месяц - проверяем
            if trans_year and trans_month:
                if trans_year == year and trans_month == month:
                    filtered_transactions.append(transaction)

        except (ValueError, IndexError) as e:
            logger.debug(f"Ошибка парсинга даты {trans_date}: {e}")
            continue

    logger.info(f"Найдено {len(filtered_transactions)} транзакций за указанный период")

    # Группируем по категориям и считаем кешбэк
    categories_cashback: Dict[Any, Any] = {}

    for transaction in filtered_transactions:
        amount = transaction.get("Сумма операции", 0)
        category = transaction.get("Категория", "Без категории")

        # Преобразуем amount в число
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            continue

        # Только расходы (отрицательные суммы)
        if amount_float < 0:
            # Кешбэк = 1% от суммы (абсолютное значение)
            cashback_amount = abs(amount_float) * 0.01

            if category in categories_cashback:
                categories_cashback[category] += cashback_amount
            else:
                categories_cashback[category] = cashback_amount

    # Сортируем по убыванию кешбэка
    sorted_categories = dict(sorted(categories_cashback.items(), key=lambda x: x[1], reverse=True))

    # Округляем до 2 знаков
    result = {k: round(v, 2) for k, v in sorted_categories.items()}

    logger.info(f"Проанализировано {len(result)} категорий")
    return result


def investment_bank(month: str, transactions: List[Dict], limit: int) -> float:
    """
    Рассчитывает сумму для Инвесткопилки через округление трат.

    ПРИНЦИП РАБОТЫ:
    - Покупка на 1712 ₽
    - Округление до 1750 ₽ (при limit=50)
    - В копилку идет: 1750 - 1712 = 38 ₽

    ПРИМЕР:
    >>> investment_bank('2024-01', transactions, 50)
    125.5  # сумма, которую можно отложить

    Аргументы:
        month: месяц в формате 'YYYY-MM' (например, '2024-01')
        transactions: список транзакций
        limit: шаг округления (10, 50 или 100 рублей)

    Возвращает:
        Сумма для Инвесткопилки
    """
    logger.info(f"💰 Расчет Инвесткопилки за {month} с округлением до {limit}")

    if limit not in [10, 50, 100]:
        logger.warning(f"Некорректный лимит округления: {limit}. Используется 50")
        limit = 50

    total_savings = 0.0
    transactions_processed = 0

    if len(month) == 7 and month[4] == "-":
        target_month = month
    else:
        try:
            if len(month) > 7:
                target_month = month[:7]
            else:
                target_month = month
        except (ValueError, TypeError) as e:
            logger.debug(f"Ошибка обработки: {e}")
            target_month = month

    logger.debug(f"Ищем транзакции за месяц: {target_month}")

    for transaction in transactions:
        try:
            # Проверяем, что транзакция за нужный месяц
            trans_date = str(transaction.get("Дата операции", ""))
            if not trans_date:
                continue
            trans_date_str = str(trans_date)
            month_found = None

            if target_month[:4] in trans_date_str:  # Ищем год в дате
                # Разные способы извлечения месяца
                if "." in trans_date_str:  # Формат ДД.ММ.ГГГГ
                    parts = trans_date_str.split(".")
                    if len(parts) >= 3:
                        month_found = f"{parts[2][:4]}-{parts[1].zfill(2)}"
                elif "-" in trans_date_str:  # Формат ГГГГ-ММ-ДД
                    parts = trans_date_str.split("-")
                    if len(parts) >= 2:
                        month_found = f"{parts[0]}-{parts[1]}"

            if month_found != target_month:
                continue

            # Берем сумму операции (отрицательную для расходов)
            amount = float(transaction.get("Сумма операции", 0))

            # Только расходы (отрицательные суммы)
            if amount < 0:
                # Округляем вверх до ближайшего кратного limit
                rounded_amount = ((abs(amount) + limit - 1) // limit) * limit

                # Считаем разницу (что пойдет в копилку)
                savings = rounded_amount - abs(amount)

                total_savings += savings
                transactions_processed += 1

                # Логируем для отладки (первые 3 транзакции)
                if transactions_processed <= 3:
                    logger.debug(f"Транзакция {abs(amount):.2f} → округлено до {rounded_amount:.2f} (+{savings:.2f})")

        except (ValueError, TypeError) as e:
            logger.warning(f"Ошибка обработки транзакции: {e}")
            continue

    logger.info(f"Обработано {transactions_processed} транзакций, сумма в копилку: {total_savings:.2f} руб.")
    return round(total_savings, 2)


def find_personal_transfers(transactions: List[Dict]) -> List[Dict]:
    """
    Ищет переводы физическим лицам.

    Критерии:
    1. Категория == 'Переводы'
    2. В описании есть имя и первая буква фамилии с точкой
       Пример: "Валерий А.", "Сергей З."
    """
    import re

    logger.info("👤 Поиск переводов физическим лицам")

    # Исправляем регулярное выражение:
    # [А-ЯЁ][а-яё]+ [А-ЯЁ]\. - находит "Имя Ф."
    # Добавляем флаг re.UNICODE и исправляем диапазоны
    pattern = re.compile(r"\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.", re.UNICODE | re.IGNORECASE)

    results = []

    for transaction in transactions:
        category = str(transaction.get("Категория", "")).strip()
        description = str(transaction.get("Описание", ""))

        # Приводим к нижнему регистру для сравнения
        if category.lower() == "переводы":
            # Ищем паттерн в описании
            if pattern.search(description):
                results.append(transaction)

    logger.info(f"Найдено {len(results)} переводов физлицам")
    return results


def find_phone_numbers(transactions: List[Dict]) -> List[Dict]:
    """Ищет транзакции с телефонными номерами в описании."""
    logger.info("Поиск транзакций с телефонными номерами")
    patterns = [
        r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}",  # Основной
        r"\b\d{3}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}\b",  # Без кода страны
    ]

    results = []
    for transaction in transactions:
        description = str(transaction.get("Описание", ""))

        for pattern in patterns:
            if re.search(pattern, description):
                results.append(transaction)
                break

    logger.info(f"Найдено {len(results)} транзакций с телефонными номерами")
    return results
