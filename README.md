# Анализатор банковских транзакций

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

Приложение для анализа банковских транзакций из Excel-файлов. Генерирует JSON-данные для веб-страниц, формирует отчеты и предоставляет сервисы для анализа финансовых операций.

## 📋 Содержание

- [Особенности](#особенности)
- [Требования](#требования)
- [Установка](#установка)
- [Конфигурация](#конфигурация)
- [Структура проекта](#структура-проекта)
- [Использование](#использование)
- [Категории заданий](#категории-заданий)
- [Тестирование](#тестирование)
- [Форматирование кода](#форматирование-кода)
- [Вклад в проект](#вклад-в-проект)
- [Лицензия](#лицензия)

## ✨ Особенности

- 📊 Анализ транзакций из Excel-файлов
- 🌐 Генерация JSON для веб-страниц
- 📈 Формирование финансовых отчетов
- 🔍 Поиск и фильтрация транзакций
- 💱 Интеграция с API курсов валют и акций
- 🧪 Полное покрытие тестами
- 📝 Логирование операций
- 🎯 Соответствие PEP 8 и лучшим практикам

## 📦 Требования

- Python 3.9 или выше
- Poetry (для управления зависимостями)
- Git

## 🚀 Установка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/ваш-username/bank-transaction-analyzer.git
cd bank-transaction-analyzer
```

2. **Установите зависимости через Poetry:**
```bash
poetry install
```

3. **Активируйте виртуальное окружение:**
```bash
poetry shell
```

Или используйте команды Poetry напрямую:
```bash
poetry run python src/main.py
```

## ⚙️ Конфигурация

### 1. Настройка переменных окружения

Создайте файл `.env` на основе шаблона:
```bash
cp .env_template .env
```

Отредактируйте `.env` файл, добавив необходимые ключи API:
```env
# API ключи для получения данных о валютах и акциях
EXCHANGE_RATE_API_KEY=ваш_ключ_для_валют
STOCK_API_KEY=ваш_ключ_для_акций

# Настройки приложения
LOG_LEVEL=INFO
DATA_FILE_PATH=data/operations.xlsx
```

### 2. Пользовательские настройки

Создайте файл `user_settings.json` для настройки отображаемых валют и акций:
```json
{
  "user_currencies": ["USD", "EUR", "GBP"],
  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}
```

### 3. Подготовка данных

Поместите ваш Excel-файл с транзакциями в папку `data/` и назовите его `operations.xlsx`.

Формат файла должен соответствовать выгрузке из Т-Банка:
- Дата операции
- Дата платежа
- Номер карты
- Статус
- Сумма операции
- Валюта операции
- Сумма платежа
- Валюта платежа
- Кешбэк
- Категория
- MCC
- Описание
- Бонусы
- Округление на «Инвесткопилку»
- Сумма операции с округлением

## 📁 Структура проекта

```
.
├── src/
│   ├── __init__.py
│   ├── utils.py             # Вспомогательные функции
│   ├── views.py             # Функции для веб-страниц
│   ├── services.py          # Сервисы анализа транзакций
│   └── reports.py           # Генерация отчетов
├── tests/
│   ├── __init__.py
│   ├── test_utils.py
│   ├── test_views.py
│   ├── test_services.py
│   └── test_reports.py
├── data/
│   └── operations.xlsx      # Файл с транзакциями
├── main.py                  # Точка входа приложения
├── .env                     # Переменные окружения (не в репозитории)
├── .env_template            # Шаблон .env файла
├── .flake8                  # Конфигурация Flake8
├── .gitignore
├── pyproject.toml          # Конфигурация Poetry и инструментов
├── poetry.lock
├── user_settings.json      # Пользовательские настройки
└── README.md
```

## 🎯 Использование

### Запуск приложения

```bash
# Активируйте виртуальное окружение
poetry shell

# Запустите основную функцию
python src/main.py

# Или используйте Poetry напрямую
poetry run python src/main.py
```

### Пример использования функций

```python
from src.views import home_page, events_page
from src.services import profitable_cashback_categories
from src.reports import spending_by_category

# Веб-страницы
home_data = home_page("2024-01-15 14:30:00")
events_data = events_page("2024-01-15", "M")

# Сервисы
transactions = [...]  # список транзакций
cashback_analysis = profitable_cashback_categories(2024, 1, transactions)

# Отчеты
import pandas as pd
df = pd.read_excel("data/operations.xlsx")
category_report = spending_by_category(df, "Супермаркеты", "2024-01-15")
```

## 📊 Категории заданий

### Веб-страницы
- **Главная** (`views.home_page`) - сводная информация по картам, топ транзакций, курсы валют
- **События** (`views.events_page`) - анализ расходов и поступлений за период

### Сервисы
- **Выгодные категории повышенного кешбэка** (`services.profitable_cashback_categories`)
- **Инвесткопилка** (`services.investment_bank`)
- **Простой поиск** (`services.simple_search`)
- **Поиск по телефонным номерам** (`services.find_phone_numbers`)
- **Поиск переводов физическим лицам** (`services.find_personal_transfers`)

### Отчеты
- **Траты по категории** (`reports.spending_by_category`)
- **Траты по дням недели** (`reports.spending_by_weekday`)
- **Траты в рабочий/выходной день** (`reports.spending_workday_vs_weekend`)

## 🧪 Тестирование

### Запуск тестов

```bash
# Запустить все тесты
pytest

# С отчетом о покрытии
pytest --cov=src --cov-report=term-missing

# Запустить конкретный тестовый файл
pytest tests/test_views.py

# С подробным выводом
pytest -v
```

### Проверка покрытия кода

Требуется покрытие не менее 80%:
```bash
pytest --cov=src --cov-report=html
```

Отчет будет сгенерирован в папке `htmlcov/`.

## 🎨 Форматирование кода

Проект использует автоматическое форматирование кода:

```bash
# Форматирование кода с Black
black src/ tests/

# Сортировка импортов с isort
isort src/ tests/

# Проверка стиля кода с Flake8
flake8 src/ tests/

# Проверка типов с mypy
mypy src/
```

Конфигурация инструментов находится в `pyproject.toml`.

## 🤝 Вклад в проект

1. Создайте форк репозитория
2. Создайте ветку для новой функциональности:
   ```bash
   git checkout -b feature/название-фичи
   ```
3. Внесите изменения и добавьте тесты
4. Проверьте код линтерами:
   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   mypy src/
   ```
5. Убедитесь, что все тесты проходят:
   ```bash
   pytest
   ```
6. Создайте Pull Request в ветку `develop`

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробнее см. в файле LICENSE.

---

## 🔗 Полезные ссылки

- [Документация Poetry](https://python-poetry.org/docs/)
- [PEP 8 — руководство по стилю Python](https://peps.python.org/pep-0008/)
- [Документация pytest](https://docs.pytest.org/)
- [Документация pandas](https://pandas.pydata.org/docs/)

## ✉️ Контакты

По вопросам и предложениям создавайте Issue в репозитории проекта.

---

*Проект разработан в рамках учебного курса по Python. Данные для анализа должны быть анонимизированы и не содержать персональную информацию.*

## 🎯 Функциональности проекта

### Веб-страницы (JSON генерация)
- ✅ **Главная страница** (`views.home_page_real`) - сводка по картам, топ транзакции, курсы валют
- ✅ **Страница "События"** (`views.events_page`) - анализ расходов/поступлений за период

### Сервисы анализа
- ✅ **Выгодные категории кешбэка** (`services.profitable_cashback_categories`)
- ✅ **Инвесткопилка** (`services.investment_bank`) - округление трат
- ✅ **Простой поиск** (`services.simple_search`) - по описанию и категории
- ✅ **Поиск по телефонным номерам** (`services.find_phone_numbers`) - regex поиск
- ✅ **Поиск переводов физлицам** (`services.find_personal_transfers`) - шаблон "Имя Ф."

### Отчеты
- ✅ **Траты по категории** (`reports.spending_by_category_simple`)
- ✅ **Траты по дням недели** (`reports.spending_by_weekday_last_year`)
- ✅ **Траты в рабочий/выходной день** (`reports.spending_workday_vs_weekend`)

### Утилиты
- ✅ **Загрузка данных** (`utils.load_transactions`) - чтение Excel с парсингом дат
- ✅ **API валют/акций** (`utils.get_currency_rates`, `utils.get_stock_prices`)
- ✅ **Пользовательские настройки** (`utils.load_user_settings`)

## 🧪 Тестирование
- Покрытие кода: 80%+ (pytest-cov)
- Моки и фикстуры для API
- Параметризованные тесты
- Тестирование крайних случаев

## 📁 Структура проекта
(оставьте существующую структуру)

## 🚀 Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <ваш-репозиторий>
cd project_1

# 2. Установить зависимости
poetry install

# 3. Настроить окружение
cp .env_template .env
# отредактируйте .env при необходимости

# 4. Создать user_settings.json
echo '{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}' > user_settings.json

# 5. Поместить файл operations.xlsx в data/

# 6. Запустить
poetry run python src/main.py

# 7. Запустить тесты
poetry run pytest tests/ -v