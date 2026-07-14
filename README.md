# FactCheckingBot

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Настройка .env

```env
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/factchecking
```

### 3. Запуск PostgreSQL

```bash
docker run -d --name postgres-factcheck \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=factchecking \
  -p 5432:5432 postgres:latest
```

### 4. Запуск бота

```bash
python bot/main.py
```