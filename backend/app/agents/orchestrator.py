from __future__ import annotations

import json
import logging
from typing import Any, Awaitable, Callable

from app.agents.prompts import AUTO_FINALIZE_PROMPT, SYSTEM_PROMPT, TOOLS
from app.config import settings
from app.core import llm as llm_module
from app.project.intent import build_user_prompt
from app.protocols.crawler import CrawledPage, CrawlerProvider
from app.protocols.search import SearchProvider
from app.schemas.search import SearchRequest
from app.schemas.tools import (
    CrawlUrlOutput,
    ExtractContactsOutput,
    FinalizeInput,
    FinalizeOutput,
    LeadDraft,
    SearchWebOutput,
)
from app.services.extraction.contact_extractor import extract_contacts
from app.services.lead_service import LeadService

logger = logging.getLogger(__name__)

StageCallback = Callable[[str, str], Awaitable[None]]


class SearchOrchestrator:
    """LLM tool-calling loop driving search -> crawl -> extract -> finalize."""

    def __init__(
        self,
        job_id: str,
        *,
        search_provider: SearchProvider,
        crawler: CrawlerProvider,
        lead_service: LeadService,
    ) -> None:
        self.job_id = job_id
        self._search = search_provider
        self._crawler = crawler
        self._leads = lead_service
        self._crawl_cache: dict[str, CrawledPage] = {}
        self._pages_crawled = 0
        self._lead_drafts: list[LeadDraft] = []
        self._last_finalize: FinalizeOutput | None = None

    async def run(
        self,
        request: SearchRequest,
        on_stage: StageCallback | None = None,
    ) -> FinalizeOutput:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(request)},
        ]
        max_pages = min(
            request.max_pages or settings.crawl_max_pages,
            settings.crawl_max_pages,
        )
        self._crawl_cache.clear()
        self._pages_crawled = 0
        self._lead_drafts = []
        self._last_finalize = None

        finalized = False
        finalize_result: FinalizeOutput | None = None

        for step in range(settings.max_tool_steps):
            response = await llm_module.completion_with_tools(messages, TOOLS)
            message = response.choices[0].message
            tool_calls = getattr(message, "tool_calls", None) or []
            content = message.content or ""

            assistant_msg: dict[str, Any] = {
                "role": "assistant",
                "content": content,
            }
            if tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in tool_calls
                ]
            messages.append(assistant_msg)

            if not tool_calls:
                if finalized:
                    break
                messages.append({"role": "system", "content": AUTO_FINALIZE_PROMPT})
                continue

            for tool_call in tool_calls:
                name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError as exc:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": (
                                f"Erro: argumentos JSON inválidos na chamada "
                                f"'{name}': {exc}"
                            ),
                        }
                    )
                    continue
                try:
                    payload = await self._dispatch(
                        name,
                        args,
                        request,
                        max_pages,
                        on_stage,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Tool %s falhou", name)
                    payload = {"error": f"Erro ao executar '{name}': {exc}"}

                if name == "finalize_results" and self._last_finalize is not None:
                    finalized = True
                    finalize_result = self._last_finalize

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(payload, ensure_ascii=False, default=str),
                    }
                )

        # Step cap reached without finalize -> auto-finalize with partial list.
        if finalize_result is None:
            await self._emit(
                on_stage,
                "synthesizing",
                "Limite de passos atingido — finalizando com leads parciais...",
            )
            await self._run_finalize(
                FinalizeInput(
                    summary="Prospecção encerrada por limite de passos do agente.",
                    leads=self._lead_drafts,
                )
            )
            finalize_result = self._last_finalize
        return finalize_result

    async def _dispatch(
        self,
        name: str,
        args: dict[str, Any],
        request: SearchRequest,
        max_pages: int,
        on_stage: StageCallback | None,
    ) -> dict[str, Any]:
        if name == "search_web":
            await self._emit(on_stage, "searching", "Buscando candidatos na web...")
            query = str(args.get("query") or request.query)
            max_results = int(args.get("max_results") or 10)
            results = await self._search.search(query, max_results=max_results)
            return SearchWebOutput(query=query, results=results).model_dump()

        if name == "crawl_url":
            await self._emit(on_stage, "crawling", "Acessando página...")
            url = str(args.get("url", "")).strip()
            if not url:
                return {"error": "URL vazia."}
            if self._pages_crawled >= max_pages:
                return {"error": f"Limite de {max_pages} páginas atingido."}
            js = bool(args.get("js", False))
            if url not in self._crawl_cache:
                page = await self._crawler.crawl(url, js=js)
                self._crawl_cache[url] = page
                self._pages_crawled += 1
            page = self._crawl_cache[url]
            preview = (page.text[:500] + "…") if page.text else None
            return CrawlUrlOutput(
                url=url,
                ok=page.ok,
                title=page.title,
                text_preview=preview,
                email_hits=page.email_hits,
                phone_hits=page.phone_hits,
                needed_js=page.needed_js,
                error=page.error,
            ).model_dump()

        if name == "extract_contacts":
            await self._emit(on_stage, "extracting", "Extraindo contatos...")
            url = str(args.get("url", "")).strip()
            js_rerun = bool(args.get("js_rerun", False))
            if not url:
                return ExtractContactsOutput(url=url, ok=False, error="URL vazia.").model_dump()
            page = self._crawl_cache.get(url)
            if page is None:
                if self._pages_crawled >= max_pages:
                    return ExtractContactsOutput(
                        url=url,
                        ok=False,
                        error=f"Limite de {max_pages} páginas atingido.",
                    ).model_dump()
                page = await self._crawler.crawl(url, js=js_rerun)
                self._crawl_cache[url] = page
                self._pages_crawled += 1
            elif js_rerun:
                page = await self._crawler.crawl(url, js=True)
                self._crawl_cache[url] = page
            if not page.ok:
                return ExtractContactsOutput(
                    url=url, ok=False, error=page.error
                ).model_dump()
            contacts = extract_contacts(page.text)
            draft = self._leads.build_lead(url, page)
            self._lead_drafts.append(draft)
            return ExtractContactsOutput(
                url=url,
                ok=True,
                name=draft.name,
                segment=draft.segment,
                city=draft.city,
                contacts=contacts,
                confidence=draft.confidence,
            ).model_dump()

        if name == "finalize_results":
            await self._emit(on_stage, "synthesizing", "Finalizando prospecção...")
            try:
                final_input = FinalizeInput.model_validate(args)
            except Exception as exc:  # noqa: BLE001 (pydantic.ValidationError)
                return {"error": f"Argumentos de finalize_results inválidos: {exc}"}
            return await self._run_finalize(final_input)

        raise ValueError(f"Ferramenta desconhecida: {name}")

    async def _run_finalize(self, final_input: FinalizeInput) -> dict[str, Any]:
        accepted, errors = self._leads.validate_and_store(self.job_id, final_input.leads)
        result = FinalizeOutput(
            ok=(not errors) or bool(accepted),
            accepted=len(accepted),
            rejected=len(errors),
            errors=errors,
        )
        self._last_finalize = result
        return {
            "ok": result.ok,
            "accepted": result.accepted,
            "rejected": result.rejected,
            "errors": result.errors,
            "message": (
                f"{result.accepted} lead(s) aceito(s), {result.rejected} rejeitado(s)."
            ),
        }

    @staticmethod
    async def _emit(
        on_stage: StageCallback | None,
        stage: str,
        message: str,
    ) -> None:
        if on_stage is None:
            return
        try:
            await on_stage(stage, message)
        except Exception:  # noqa: BLE001
            logger.exception("Callback on_stage falhou (stage=%s)", stage)
