"""
Тесты для утилит.
"""

import sys
from pathlib import Path
from unittest.mock import mock_open, patch

from src.utils import get_greeting, load_user_settings

sys.path.insert(0, str(Path(__file__).parent / ".." / "src"))


def test_load_user_settings() -> None:
    """Тест загрузки пользовательских настроек."""
    test_json = '{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}'

    with patch("builtins.open", mock_open(read_data=test_json)):
        result = load_user_settings()

    assert "user_currencies" in result
    assert "user_stocks" in result
    assert result["user_currencies"] == ["USD"]


def test_load_user_settings_file_not_found() -> None:
    """Тест загрузки настроек при отсутствии файла."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = load_user_settings()

    assert "user_currencies" in result
    assert len(result["user_currencies"]) > 0


def test_get_greeting() -> None:
    """Тест определения приветствия."""
    test_case = [
        ("05:30:00", "Доброй ночи"),
        ("08:00:00", "Доброе утро"),
        ("14:00:00", "Добрый день"),
        ("19:00:00", "Добрый вечер"),
        ("23:30:00", "Доброй ночи"),
    ]
    for time_str, expected in test_case:
        result = get_greeting(time_str)
        assert result == expected, f"Для {time_str} ожидалось {expected}, получено {result}"
