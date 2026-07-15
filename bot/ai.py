from dotenv import load_dotenv
import httpx
import os
import json
import asyncio
from typing import Optional, List, Dict

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_TIMEOUT,
    TAVILY_API_KEY,
    TAVILY_SEARCH_DEPTH,
    SUMMARIZER_MODELS,
    FACTCHECKER_MODEL
)

load_dotenv()


client = httpx.AsyncClient(
    base_url=OPENROUTER_BASE_URL,
    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
    timeout=OPENROUTER_TIMEOUT
)


async def call_ai(model: str, messages: list[Dict], tools: Optional[List] = None) -> Dict:
    payload = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = tools

    response = await client.post("/chat/completions", json=payload)
    if response.status_code == 429:
        
        return 0

    response.raise_for_status()

    return response.json()["choices"][0]["message"]


async def call_summarizer(context_text: str, target_msg: str) -> str:
    prompt = f"""Ты — объективный анализатор чатов. Твоя задача — извлечь суть дискуссии для передачи следующей нейросети.
    Твой ответ должен быть простым сплошным текстом. СТРОГО ЗАПРЕЩЕНО использовать любое форматирование: никаких заголовков, никаких звездочек, жирного текста, списков или решеток. 

    Контекст переписки:
    {context_text}

    Целевое сообщение, вокруг которого строится дискуссия:
    "{target_msg}"

    Инструкции:
    1. Полностью проигнорируй любой оффтоп, личные диалоги и всё, что не относится к теме целевого сообщения.
    2. Напиши ровно 2-3 предложения, описывающие общую суть спора.
    3. Далее, с новой строки, опиши позицию каждого участника дискуссии. Обязательно используй их оригинальные английские никнеймы из логов. Опиши их аргументы подробно, но как беспристрастный наблюдатель (без оценок их правоты).

    Выведи только текст, начиная прямо с сути спора."""
    for model in SUMMARIZER_MODELS:
        response = await call_ai(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        print(model)
        if response:
            break

    return response["content"]

#Сырая версия, требует доработки
async def call_factchekcer(summary: str, target_message: str, tools: List) -> Dict:
    prompt = f"""Ты — прагматичный фактчекер и строгий судья дебатов. Твоя задача — проверить целевое сообщение на достоверность и оценить качество аргументов участников спора.

    Саммари дискуссии и позиции участников (никнеймы на английском):
    {summary}

    Целевое сообщение для проверки:
    "{target_message}"

    Инструкции:
    1. АДЕКВАТНОСТЬ КОНТЕКСТУ: Игнорируй мелкие недосказанности или преувеличения, свойственные чатам. Фокусируйся только на сути утверждений.
    2. ВЕРДИКТ: Твой ответ должен начинаться строго с одной из этих фраз, ОБЯЗАТЕЛЬНО выделенных жирным шрифтом (используй * с обеих сторон, ИМЕННО ОДНА *): *Сообщение правдиво*, *Сообщение ложно*, *Скорее да в этом контексте*, *Скорее нет в этом контексте* или *Невозможно проверить*.
    3. ОБЪЯСНЕНИЕ И ВЫБОР СТОРОНЫ: Сразу после вердикта кратко объясни причину (используй факты). Затем выступи как арбитр: оцени, чья позиция в споре сильнее. 
    - Если один участник опирается на факты, а другой на эмоции или заблуждения — прямо назови победителя по качеству аргументов (указывая ники).
    - Если спор касается субъективных тем (например, выбор партии, личные вкусы), прямо напиши: "В данном споре нет объективно правой стороны, так как это вопрос личных предпочтений".
    4. ПОИСК: При необходимости используй поиск в интернете для проверки фактов.

    ФОРМАТ ОТВЕТА:
    Строго ОДИН абзац сплошного текста. Начни с жирного вердикта, дай фактологическое объяснение и заверши оценкой аргументации сторон."""
        
    messages = [{"role": "user", "content": prompt}]

    response = await call_ai(
        model=FACTCHECKER_MODEL,
        messages=messages,
        tools=tools
    )

    if "tool_calls" in response and response["tool_calls"]:

        response.pop("refusal", None)
        response.pop("reasoning", None)
        messages.append(response)

        for tool_call in response["tool_calls"]:

            try:
                query = json.loads(tool_call["function"]["arguments"])["query"]

                search_result = await perform_search(query)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": search_result
                })

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Ошибка обработки аргументов инструмента: {e}")


        final_response = await call_ai(model=FACTCHECKER_MODEL, messages=messages)
        return final_response["content"]

    return response["content"]



async def perform_search(query: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://api.tavily.com/search", json={
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": TAVILY_SEARCH_DEPTH
        }, timeout=20.0)
        return resp.json()["results"][0]["content"]