from __future__ import annotations

import asyncio
import logging
from typing import Any

import litellm

from app.config import settings

logger = logging.getLogger(__name__)


def _build_kwargs(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 2048,
        "timeout": 60,
    }
    if settings.llm_api_base:
        kwargs["api_base"] = settings.llm_api_base
    if settings.llm_api_key:
        kwargs["api_key"] = settings.llm_api_key
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    return kwargs


def _completion_sync(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
) -> Any:
    return litellm.completion(**_build_kwargs(messages, tools))


async def completion_with_tools(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> Any:
    """Call the LLM with function-calling tools. 2 retries with exponential backoff."""
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            return await asyncio.to_thread(_completion_sync, messages, tools)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < 2:
                delay = 1.0 * (2**attempt)
                logger.warning(
                    "LLM call failed (attempt %d/%d): %s — retrying in %.1fs",
                    attempt + 1,
                    3,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
    raise RuntimeError(f"Falha ao chamar o modelo de linguagem: {last_error}") from last_error


async def complete(messages: list[dict[str, Any]]) -> str:
    """Plain completion used for synthesis; returns the model's text content."""
    response = await asyncio.to_thread(_completion_sync, messages, None)
    return response.choices[0].message.content or ""
