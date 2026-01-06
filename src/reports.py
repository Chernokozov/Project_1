"""
Простые отчеты.
"""

import logging
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict

import pandas as pd

from src.file_utils import get_reports_dir, save_json_file

logger = logging.getLogger(__name__)


def report_to_file(filename: str = "report.json"):
    """
    Простой декоратор для сохранения отчета в файл
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Выполняем функцию
            result = func(*args, **kwargs)

            # Генерируем имя файла если не указано
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_name = func.__name__
                output_filename = get_reports_dir() / f"{report_name}_{timestamp}.json"
            else:
                output_filename = Path(filename)

            # Сохраняем результат в файл
            save_json_file(result, output_filename)

            return result

        return wrapper

    return decorator


@report_to_file("spending_report.json")
def spending_by_category_simple(df: pd.DataFrame, category: str) -> Dict[str, Any]:
    """
    Простой отчет по тратам в категории.
    :param df:
    :param category:
    :return:
    """
    logger.info(f"Анализ категории:{category}")

    category_data = df[df["Категория"] == category]
    if category_data.empty:
        return {
            "category": category,
            "total_spent": 0,
            "transaction_count": 0,
            "message": "Нет транзакций в этой категории",
        }
    expenses = category_data[category_data["Сумма операции"] < 0]
    total_spent = abs(expenses["Сумма операции"].sum())

    result = {
        "category": category,
        "total_spent": round(total_spent, 2),
        "transaction_count": len(expenses),
        "average_per_transaction": round(total_spent / len(expenses), 2) if len(expenses) > 0 else 0,
        "period": {"start": str(df["Дата операции"].min())[:10], "end": str(df["Дата операции"].max())[:10]},
    }

    logger.info(f"В категории '{category}' потрачено {result['total_spent']} руб.")
    return result


def spending_by_weekday(df: pd.DataFrame, date: str = None) -> Dict[str, Any]:
    """
    Анализ средних трат по дням недели за последние 3 месяца.
    """
    logger.info("📅 Анализ трат по дням недели")

    if df is None or df.empty:
        logger.warning("Пустой DataFrame передан в функцию")
        return {"error": "Пустые данные", "workdays": {}, "weekends": {}}

    try:
        # Проверяем что df не пустой
        if df.empty:
            return {"error": "Нет данных для анализа", "period": "N/A"}

        # Создаем копию чтобы не менять оригинал
        df_copy = df.copy()

        # Преобразуем дату если нужно
        if date is None:
            end_date = datetime.now()
        else:
            end_date = pd.to_datetime(date)

        # Дата 3 месяца назад
        start_date = end_date - pd.DateOffset(months=3)

        # Убедимся что даты в правильном формате
        if "Дата операции" not in df_copy.columns:
            return {"error": 'Колонка "Дата операции" не найдена'}

        # Преобразуем даты если они еще не в datetime
        if not pd.api.types.is_datetime64_any_dtype(df_copy["Дата операции"]):
            try:
                df_copy["Дата операции"] = pd.to_datetime(df_copy["Дата операции"], dayfirst=True, errors="coerce")
            except (ValueError, TypeError) as e:
                return {"error": f"Не удалось преобразовать даты: {e}"}

        # Фильтруем по периоду и только расходы
        mask = (
            (df_copy["Дата операции"] >= start_date)
            & (df_copy["Дата операции"] <= end_date)
            & (df_copy["Сумма операции"] < 0)
        )

        filtered_df = df_copy.loc[mask].copy()

        if filtered_df.empty:
            return {
                "error": "Нет данных за указанный период",
                "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            }

        # Добавляем день недели и название дня
        filtered_df["day_of_week"] = filtered_df["Дата операции"].dt.dayofweek
        filtered_df["day_name"] = filtered_df["Дата операции"].dt.day_name()

        # Русские названия дней
        day_names_ru = {
            0: "Понедельник",
            1: "Вторник",
            2: "Среда",
            3: "Четверг",
            4: "Пятница",
            5: "Суббота",
            6: "Воскресенье",
        }

        # Группируем по дням недели
        daily_stats = {}
        total_spent = 0

        for day_num in range(7):
            day_data = filtered_df[filtered_df["day_of_week"] == day_num]

            if len(day_data) > 0:
                # Средняя трата в этот день недели
                avg_spent = abs(day_data["Сумма операции"].mean())
                daily_stats[day_names_ru[day_num]] = round(avg_spent, 2)
                total_spent += abs(day_data["Сумма операции"].sum())

        # Сортируем по убыванию трат
        sorted_daily = dict(sorted(daily_stats.items(), key=lambda x: x[1], reverse=True))

        # Общая статистика
        total_days = len(filtered_df["Дата операции"].dt.date.unique())

        result = {
            "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            "total_days_analyzed": total_days,
            "total_transactions": len(filtered_df),
            "total_spent": round(total_spent, 2),
            "average_per_day": round(total_spent / total_days, 2) if total_days > 0 else 0,
            "by_weekday": sorted_daily,
            "most_expensive_day": list(sorted_daily.keys())[0] if sorted_daily else "Нет данных",
            "cheapest_day": list(sorted_daily.keys())[-1] if sorted_daily else "Нет данных",
        }

        logger.info(f"Проанализировано {len(filtered_df)} транзакций за {total_days} дней")
        return result

    except Exception as e:
        logger.error(f"Ошибка анализа по дням недели: {e}")
        return {"error": str(e), "workdays": {}, "weekends": {}}


def spending_by_weekday_last_year(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Анализ трат по дням недели за последний год из данных.
    Анализирует последние 12 месяцев от максимальной даты в данных.
    """
    logger.info("📅 Анализ трат по дням недели за последний год из данных")

    try:
        if df.empty or "Дата операции" not in df.columns:
            return {"error": "Нет данных для анализа"}

        df_copy = df.copy()

        # Убедимся что даты в правильном формате
        if not pd.api.types.is_datetime64_any_dtype(df_copy["Дата операции"]):
            df_copy["Дата операции"] = pd.to_datetime(df_copy["Дата операции"], dayfirst=True, errors="coerce")

        # Находим максимальную дату в данных
        max_date = df_copy["Дата операции"].max()
        if pd.isna(max_date):
            return {"error": "Не удалось определить максимальную дату"}

        # Дата 12 месяцев назад от максимальной даты в данных
        start_date = max_date - pd.DateOffset(months=12)

        # Фильтруем по периоду и только расходы
        mask = (
            (df_copy["Дата операции"] >= start_date)
            & (df_copy["Дата операции"] <= max_date)
            & (df_copy["Сумма операции"] < 0)
        )

        filtered_df = df_copy.loc[mask].copy()

        if filtered_df.empty:
            # Форматируем даты для читаемости
            data_start = df_copy["Дата операции"].min().strftime("%Y-%m-%d")
            data_end = max_date.strftime("%Y-%m-%d")
            analyzed_start = start_date.strftime("%Y-%m-%d")

            return {
                "error": "Нет расходов за последний год из данных",
                "data_period": f"{data_start} - {data_end}",
                "analyzed_period": f"{analyzed_start} - {data_end}",
            }

        # Добавляем день недели
        filtered_df["day_of_week"] = filtered_df["Дата операции"].dt.dayofweek

        # Русские названия дней
        day_names_ru = {
            0: "Понедельник",
            1: "Вторник",
            2: "Среда",
            3: "Четверг",
            4: "Пятница",
            5: "Суббота",
            6: "Воскресенье",
        }

        # Группируем по дням недели
        daily_stats = {}

        for day_num in range(7):
            day_data = filtered_df[filtered_df["day_of_week"] == day_num]

            if len(day_data) > 0:
                # Средняя трата в этот день недели
                avg_spent = abs(day_data["Сумма операции"].mean())
                daily_stats[day_names_ru[day_num]] = round(avg_spent, 2)

        # Сортируем
        sorted_daily = dict(sorted(daily_stats.items(), key=lambda x: x[1], reverse=True))

        # Общая статистика
        total_spent = abs(filtered_df["Сумма операции"].sum())
        total_days = len(filtered_df["Дата операции"].dt.date.unique())

        result = {
            "period": f"{start_date.strftime('%Y-%m-%d')} - {max_date.strftime('%Y-%m-%d')}",
            "total_days_analyzed": total_days,
            "total_transactions": len(filtered_df),
            "total_spent": round(total_spent, 2),
            "average_per_day": round(total_spent / total_days, 2) if total_days > 0 else 0,
            "by_weekday": sorted_daily,
            "most_expensive_day": list(sorted_daily.keys())[0] if sorted_daily else "Нет данных",
            "cheapest_day": list(sorted_daily.keys())[-1] if sorted_daily else "Нет данных",
            "note": "Анализ за последний год из доступных данных",
        }

        logger.info(f"Проанализировано {len(filtered_df)} транзакций за {total_days} дней")
        return result

    except Exception as e:
        logger.error(f"Ошибка анализа по дням недели: {e}")
        return {"error": str(e)}


def spending_workday_vs_weekend(df: pd.DataFrame, date: str = None) -> Dict[str, Any]:
    """
    Анализ средних трат в рабочие/выходные дни за последние 3 месяца.
    """
    logger.info("Анализ трат в рабочие/выходные дни")

    try:
        if df.empty or "Дата операции" not in df.columns:
            return {"error": "Нет данных для анализа"}

        df_copy = df.copy()

        if date is None:
            end_date = datetime.now()
        else:
            end_date = pd.to_datetime(date)

        start_date = end_date - pd.DateOffset(months=3)

        if not pd.api.types.is_datetime64_any_dtype(df_copy["Дата операции"]):
            df_copy["Дата операции"] = pd.to_datetime(df_copy["Дата операции"], dayfirst=True, errors="coerce")

        # Исправлено: убрал лишнюю скобку и сдвинул код на правильный уровень
        mask = (
            (df_copy["Дата операции"] >= start_date)
            & (df_copy["Дата операции"] <= end_date)
            & (df_copy["Сумма операции"] < 0)
        )

        filtered_df = df_copy.loc[mask].copy()

        if filtered_df.empty:
            return {
                "error": "Нет расходов за указанный период",
                "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            }

        filtered_df["day_of_week"] = filtered_df["Дата операции"].dt.dayofweek
        filtered_df["is_weekend"] = filtered_df["day_of_week"] >= 5
        workdays_df = filtered_df[~filtered_df["is_weekend"]]
        weekends_df = filtered_df[filtered_df["is_weekend"]]

        # Исправлено: добавлено вычисление average_per_day для выходных
        workdays_stats = {
            "total_spent": abs(workdays_df["Сумма операции"].sum()),
            "transaction_count": len(workdays_df),
            "average_per_day": abs(workdays_df["Сумма операции"].mean()) if len(workdays_df) > 0 else 0,
            "days_count": len(workdays_df["Дата операции"].dt.date.unique()),
        }

        weekends_stats = {
            "total_spent": abs(weekends_df["Сумма операции"].sum()),
            "transaction_count": len(weekends_df),  # Исправлено: было abs(weekends_df["Сумма операции"].mean())
            "average_per_day": abs(weekends_df["Сумма операции"].mean()) if len(weekends_df) > 0 else 0,  # Добавлено
            "days_count": len(weekends_df["Дата операции"].dt.date.unique()),
        }

        total_stats = {
            "workdays_percentage": (
                round(
                    workdays_stats["total_spent"]
                    / (workdays_stats["total_spent"] + weekends_stats["total_spent"])
                    * 100,
                    1,
                )
                if (workdays_stats["total_spent"] + weekends_stats["total_spent"]) > 0
                else 0
            ),
            "difference_percentage": (
                round(
                    (workdays_stats["average_per_day"] - weekends_stats["average_per_day"])
                    / max(workdays_stats["average_per_day"], weekends_stats["average_per_day"])
                    * 100,
                    1,
                )
                if max(workdays_stats["average_per_day"], weekends_stats["average_per_day"]) > 0
                else 0
            ),
        }

        result = {
            "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            "workdays": {k: round(v, 2) if isinstance(v, float) else v for k, v in workdays_stats.items()},
            "weekends": {k: round(v, 2) if isinstance(v, float) else v for k, v in weekends_stats.items()},
            "comparison": total_stats,
            "summary": {
                "more_spent_on": (
                    "workdays" if workdays_stats["average_per_day"] > weekends_stats["average_per_day"] else "weekends"
                ),
                "workdays_avg": round(workdays_stats["average_per_day"], 2),
                "weekends_avg": round(weekends_stats["average_per_day"], 2),
            },
        }

        logger.info(
            f"Проанализировано {len(filtered_df)} транзакций: {len(workdays_df)} рабочих, "
            f"{len(weekends_df)} выходных"
        )
        return result

    except Exception as e:
        logger.error(f"Ошибка анализа рабочих/выходных дней: {e}")
        return {"error": str(e)}
