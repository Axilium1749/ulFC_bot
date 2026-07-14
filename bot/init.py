import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

env_path = project_root / ".env"
example_path = project_root / ".env.example"

def show_error_and_exit(missing_keys):
    """Выводит инструкцию и завершает работу скрипта."""
    print(f"!!! ОШИБКА: Не заданы переменные: {', '.join(missing_keys)}")
    print("ИНСТРУКЦИЯ:")
    print("1. Отредактируйте файл .env в папке проекта.")
    print("2. Впишите туда реальные ключи.")
    print("3. Перезапустите контейнер: docker-compose down && docker-compose up -d")
    sys.exit(1)

if not env_path.exists():
    if example_path.exists():
        shutil.copy(example_path, env_path)
        show_error_and_exit(["BOT_TOKEN", "OPENROUTER_API_KEY", "TAVILY_API_KEY"])
    else:
        print("!!! ОШИБКА: Не найден шаблон .env.example.")
        sys.exit(1)

load_dotenv(dotenv_path=env_path)

required_keys = ["BOT_TOKEN", "OPENROUTER_API_KEY", "TAVILY_API_KEY"]
missing = [key for key in required_keys if not os.getenv(key) or os.getenv(key) == "None"]

if missing:
    show_error_and_exit(missing)