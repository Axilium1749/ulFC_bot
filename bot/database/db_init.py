import asyncio
from db import init_db

async def main():
    try:
        print("Подключаюсь к базе и создаю таблицы...")
        await init_db()
        print("Успешно!")
    except Exception as e:
        print(f"ОШИБКА: {e}")

if __name__ == "__main__":
    asyncio.run(main())