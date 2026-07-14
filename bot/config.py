"""
Конфигурация проекта FactCheckingBot.

Содержит все настройки: модели AI, API ключи, база данных, таймауты и другие параметры.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# =============================================================================
# API Ключи
# =============================================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
DATABASE_URL=os.getenv("DATABASE_URL")

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

    # AI Модели
    "SUMMARIZER_MODEL",
    "FACTCHECKER_MODEL",
    "FACTCHECKER_FINAL_MODEL",

    # OpenRouter Настройки
    "OPENROUTER_BASE_URL",
    "OPENROUTER_TIMEOUT",

    # Tavily Настройки
    "TAVILY_SEARCH_DEPTH",

    # AI Инструменты
    "TOOLS",

    # База Данных
    "DATABASE_URL",

    # Сессии и Таймауты
    "SESSION_THRESHOLD",
    "TIME_WINDOW",
]