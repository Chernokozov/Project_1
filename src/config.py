"""
Конфигурация приложения.
"""
import logging
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / 'data'/ 'operations.xlsx'
REPORTS_DIR = PROJECT_ROOT / 'reports'

DEFAULT_SETTINGS: Dict[str, Any] = {
    "user_currencies": ["USD", "EUR"],
    "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}

EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY', '')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')

EXCHANGE_RATE_URL = "https://api.exchangerate-api.com/v4/latest/RUB"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
FINNHUB_URL = "https://finnhub.io/api/v1"

MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))

# Настройки API (заглушки)
FALLBACK_CURRENCY_RATES: Dict[str, float] = {
    'USD': 90.5,
    'EUR': 99.2,
    'GBP': 115.0,
    'CNY': 12.5,
    'JPY': 0.62
}

FALLBACK_STOCK_PRICES: Dict[str, float] = {
    'AAPL': 185.30,
    'GOOGL': 145.20,
    'MSFT': 375.50,
    'TSLA': 250.75,
    'AMZN': 155.80,
    'META': 350.25,
    'NVDA': 495.00
}


def setup_logging(level: int = LOG_LEVEL) -> None:
    """Настраивает  логирование."""
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(PROJECT_ROOT / 'app.log', encoding='utf-8')
        ]
    )
