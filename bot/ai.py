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


async def call_summarizer(context_text: str, target_msg:str) -> str:
    prompt = f"""Ты — аналитик дискуссий, работающий в связке с фактчекером. 
    Твоя задача: объективно суммаризировать спор, отсекая все, что не относится к существу дела. 
    Твоя задача — быть «зеркалом», передавая позиции участников без искажений и сглаживания. Никаких собственных мнений.

    Контекст переписки:
    {context_text}

    Целевое сообщение, вокруг которого строится дискуссия:
    "{target_msg}"

    Твои инструкции:
    1. ФИЛЬТРАЦИЯ: Игнорируй любые сообщения или реплики, которые не относятся к предмету обсуждения целевого сообщения. Если сообщение — это оффтоп, личная переписка или технические моменты, не связанные с темой {target_msg}, полностью исключи их из анализа.
    2. УЧАСТНИКИ И ПОЗИЦИИ: Составь список участников спора. Для каждого укажи его четкую позицию (аргументы, которые он защищает) относительно обсуждаемого вопроса. 
    3. СУТЬ СПОРА: Сформулируй кратко, в чем именно заключается разногласие.
    4. КЛЮЧЕВЫЕ УТВЕРЖДЕНИЯ: Выпиши все утверждения (факты, цифры, логические выводы), претендующие на истинность, которые были озвучены участниками. Обязательно указывай, кто именно сделал утверждение.

    Формат ответа:
    ### Участники и их позиции
    - [Имя]: [Краткое изложение позиции]
    ### Предмет спора
    [Краткое описание сути разногласий]
    ### Ключевые утверждения для проверки
    - [Кто]: [Утверждение]
    - [Кто]: [Утверждение]

    Важно: передавай содержание максимально близко к источнику, не пытаясь примирить стороны. Фактчекеру нужна точность позиций для проверки."""

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
    prompt = f"""Ты — бескомпромиссный фактчекер. Твоя задача — провести критический разбор сообщения на предмет точности, манипуляций или фактических ошибок. 

    Саммари контекста дискуссии:
    {summary}

    Целевое сообщение для анализа:
    "{target_message}"

    Инструкции по анализу:
    1. КРИТИКА: Ищи в сообщении логические ошибки, подмену понятий, вырванные из контекста цитаты или эмоциональные манипуляции. Твоя цель — вскрыть манипуляцию, а не смягчить углы.
    2. ВЕРИФИКАЦИЯ: Если в сообщении есть утверждения о фактах, событиях или цифрах, используй инструмент google_search для поиска опровержений или подтверждений в авторитетных источниках.
    3. ОЦЕНКА МНЕНИЙ: Если сообщение выражает мнение, оцени его степень аргументированности. Является ли оно взвешенным или это радикальная позиция, не подкрепленная логикой или данными?
    4. ВЕРДИКТ: Твой вывод должен быть резким и однозначным. Не используй теги типа [ДОСТОВЕРНО] или [ЛОЖНО]. Вместо этого прямо напиши в конце, является ли информация фактической ошибкой, намеренным искажением (фейком), натянутым суждением или обоснованным аргументом.

    Формат ответа:
    - Анализ аргументации и контекста (почему это сказано и что скрыто).
    - Фактическая проверка (что подтверждается, а что опровергается поиском).
    - Итоговый вердикт (максимум 2-3 абзаца, прямое утверждение о статусе сообщения).

    Действуй как эксперт, для которого истина важнее вежливости. Если данных недостаточно, четко укажи, чего именно не хватает для однозначного вывода."""

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