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


async def call_summarizer(context_text: str) -> str:
    prompt = f"""Ты — аналитик дискуссий. Твоя задача: кратко резюмировать суть спора и ключевые утверждения, которые требуют проверки.
    Проанализируй следующий контекст переписки:

    {context_text}

    Выдели:
    1. Краткое описание предмета спора.
    2. Список конкретных утверждений (фактов), высказанных участниками, которые звучат как претендующие на истину.
    3. Если дискуссия содержит противоречивые данные, укажи это.

    Отвечай максимально сжато."""

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
    prompt = f"""Ты — профессиональный фактчекер. Твоя цель — определить, является ли утверждение из сообщения достоверным.

    Саммари дискуссии:
    {summary}

    Сообщение для проверки:
    {target_message}

    Инструкция:
    1. Проанализируй сообщение на соответствие реальности и здравому смыслу.
    2. Если в сообщении содержится конкретный факт (дата, событие, цифра, закон), который невозможно подтвердить только из саммари, ОБЯЗАТЕЛЬНО используй инструмент поиска (google_search), чтобы верифицировать это утверждение.
    3. Если утверждение явно ложное или противоречит общеизвестным данным, опровергни его с кратким объяснением.
    4. В ответе дай вердикт: [ДОСТОВЕРНО], [ЛОЖНО] или [МНЕНИЕ].
    5. Не пытайся угодить всем, вырази объективную позицию либо оцени субъективную, если объективности в предмете спора быть не может.
    Если данных для проверки недостаточно, так и напиши."""

    messages = [{"role": "user", "content": prompt}]

    response = await call_ai(
        model=FACTCHECKER_MODEL,
        messages=messages,
        tools=tools
    )

    if "tool_calls" in response:
        tool_call = response["tool_calls"][0]
        query = json.loads(tool_call["function"]["arguments"])["query"]

        search_result = await perform_search(query)

        messages.append(response)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": search_result
        })

        final_response = await call_ai(model=FACTCHECKER_MODEL, messages=messages)
        return final_response["content"]

    return response["content"]



async def perform_search(query: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://api.tavily.com/search", json={
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": TAVILY_SEARCH_DEPTH
        })
        return resp.json()["results"][0]["content"]