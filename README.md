# FactCheckingBot

## Быстрый старт


### 1. Запуск

```bash
sudo docker compose up -d --build
```

### 2. Остановка

```bash
sudo docker compose down
```

### 3. Просмотр логов

```bash
sudo docker compose logs -f bot
```

### 4. Перезапуск

```bash
sudo docker compose down
sudo docker compose up -d --build
```

### 5. Настройка .env

Настройки `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/factchecker_db
```
