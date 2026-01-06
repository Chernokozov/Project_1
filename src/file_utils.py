"""
Утилиты для работы с файлами и путями.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Возвращает корневую директорию проекта."""
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """Возвращает путь к директории с данными."""
    data_dir = get_project_root() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_reports_dir() -> Path:
    """Возвращает путь к директориям с отчетами."""
    reports_dir = get_project_root() / "reports"
    reports_dir.mkdir(exist_ok=True)
    return reports_dir


def load_json_file(file_path: Path) -> Any:
    """
    Загружает JSON файл.
    """
    try:
        if not file_path.exists():
            logger.warning(f"Файл {file_path} не найден")
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"Файл {file_path} успешно загружен.")
        return data
    except Exception as e:
        logger.error(f"Ошибка загрузки файла {file_path}:{e}")
        return {}


def save_json_file(data: Dict[str, Any], file_path: Path) -> bool:
    """
    Сохраняем данные в JSON файл.
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Данные сохранены в {file_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения файла {file_path}: {e}")
        return False
