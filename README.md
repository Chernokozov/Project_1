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
poetry run python main.py
```

## ⚙️ Конфигурация
### 1. Настройка переменных окружения
Создайте файл `.env` на основе шаблона:
```bash
cp .env_template .env
```
Отредактируйте `.env` файл:
```env
# API ключи для получения данных о валютах и акциях
EXCHANGE_RATE_API_KEY=ваш_ключ_для_валют
STOCK_API_KEY=ваш_ключ_для_акций

# Настройки приложения
LOG_LEVEL=INFO
DATA_FILE_PATH=data/operations.xlsx
```

### 2. Пользовательские настройки
Создайте файл `user_settings.json`:
```json
{
  "user_currencies": ["USD", "EUR", "GBP"],
  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}
```

### 3. Подготовка данных
Поместите ваш Excel-файл с транзакциями в папку `data/` и назовите его `operations.xlsx`.

## 📁 Структура проекта
```
├── .env_template
├── .flake8
├── .gitignore
├── data/
│   └── operations.xlsx
├── main.py
├── poetry.lock
├── pyproject.toml
├── README.md
├── src/
│   ├── __init__.py
│   ├── api_utils.py
│   ├── config.py
│   ├── file_utils.py
│   ├── reports.py
│   ├── services.py
│   ├── utils.py
│   └── views.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api_utils.py
│   ├── test_reports.py
│   ├── test_services.py
│   ├── test_utils.py
│   └── test_views.py
└── user_settings.json
```

## 🎯 Использование
### Запуск приложения
```bash
# Используя Poetry (рекомендуется)
poetry run python main.py

# Или активировав виртуальное окружение
poetry shell
python main.py
```

## 📊 Категории заданий
### Веб-страницы
- **Главная** (`views.home_page_real`) - сводная информация по картам, топ транзакций, курсы валют
- **События** (`views.events_page`) - анализ расходов и поступлений за период

### Сервисы
- **Выгодные категории повышенного кешбэка** (`services.profitable_cashback_categories`)
- **Инвесткопилка** (`services.investment_bank`)
- **Простой поиск** (`services.simple_search`)
- **Поиск по телефонным номерам** (`services.find_phone_numbers`)
- **Поиск переводов физическим лицам** (`services.find_personal_transfers`)

### Отчеты
- **Траты по категории** (`reports.spending_by_category_simple`)
- **Траты по дням недели** (`reports.spending_by_weekday_last_year`)
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
```
