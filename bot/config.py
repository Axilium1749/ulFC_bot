"""
Конфигурация проекта FactCheckingBot.

Содержит все настройки: модели AI, API ключи, база данных, таймауты и другие параметры.
"""

import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


def _validate_env_vars():
    """
    Проверяет наличие обязательных переменных окружения.
    Если чего-то не хватает - выводит сообщение об ошибке и завершает программу с кодом 1.
    """
    required_vars = [
        "BOT_TOKEN",
        "OPENROUTER_API_KEY",
        "TAVILY_API_KEY",
        "DATABASE_URL",
    ]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value is None or value == "None" or value == "":
            missing_vars.append(var)

    if missing_vars:
        print(f"Ошибка: Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}", file=sys.stderr)
        sys.exit(1)


# Проверяем обязательные переменные перед их использованием
_validate_env_vars()

# =============================================================================
# API Ключи
# =============================================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# =============================================================================
# AI Модели
# =============================================================================

# Модель для суммаризации текста
SUMMARIZER_MODELS = ["google/gemma-4-31b-it:free",
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "qwen/qwen3-next-80b-a3b-instruct:free",
                    "openai/gpt-4o-mini"]


# Модель для fact-checking (начальный запрос с поиском)
FACTCHECKER_MODEL = "openai/gpt-4o-mini"

# =============================================================================
# OpenRouter API Настройки
# =============================================================================

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_TIMEOUT = 60.0  # секунд

# =============================================================================
# Tavily API Настройки
# =============================================================================

TAVILY_SEARCH_DEPTH = "advanced"

# =============================================================================
# AI Инструменты (Tools)
# =============================================================================

TOOLS = [{
    "type": "function",
    "function": {
        "name": "google_search",
        "description": "Поиск информации в интернете для проверки фактов",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Поисковый запрос"}
            },
            "required": ["query"]
        }
    }
}]

# =============================================================================
# Настройки Сессий и Таймаутов
# =============================================================================

# Порог затишья между сессиями (30 минут)
SESSION_THRESHOLD = timedelta(minutes=30)
TIME_WINDOW = timedelta(minutes=30)

# =============================================================================
# Экспорт констант для удобства
# =============================================================================

__all__ = [
    # API Ключи
    "BOT_TOKEN",
    "OPENROUTER_API_KEY",
    "TAVILY_API_KEY",
    "DATABASE_URL",

    # AI Модели
    "SUMMARIZER_MODELS",
    "FACTCHECKER_MODEL",

    # OpenRouter Настройки
    "OPENROUTER_BASE_URL",
    "OPENROUTER_TIMEOUT",

    # Tavily Настройки
    "TAVILY_SEARCH_DEPTH",

    # AI Инструменты
    "TOOLS",

    # Сессии и Таймауты
    "SESSION_THRESHOLD",
    "TIME_WINDOW",
]