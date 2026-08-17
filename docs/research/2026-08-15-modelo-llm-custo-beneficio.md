# Pesquisa — Melhor modelo LLM pago (custo/benefício) para o scrapAI

**Data:** 15/08/2026 · **Agente:** researcher · **Status:** pesquisa concluída

## Contexto analisado

- Pipeline agêntico de prospecção B2B (loop de tool calling com até 15 passos/job).
- Cada job: ~60k tokens de input + ~15k tokens de output (estimado: 15 chamadas × ~4k in / 1k out).
- LiteLLM (API compatível OpenAI). Modelo atual: `gpt-4o-mini` (`backend/app/config.py`).
- Necessidades: function calling forte, bom português, custo/token crítico (volume alto), contexto de prompts de sistema grandes.

## Ranking final (ago/2026)

| Modelo | Preço 1M in/out | Custo/job | Jobs/dia com US$ 50/mês | Notas |
|---|---|---|---|---|
| 🥇 **DeepSeek V4 Flash** | US$ 0,14 / US$ 0,28 | ~US$ 0,013 | ~130–200 | Melhor tool-use multi-turn por dólar; contexto 1M; sem RPM |
| 🥈 **GPT-5 mini** | US$ 0,25 / US$ 2,00 | ~US$ 0,045 | ~37–44 | Migração zero (mesma API OpenAI); fallback recomendado |
| Claude Sonnet 5 | US$ 3,00 / US$ 15,00 (promo US$ 2/10 até 31/08/2026) | ~US$ 0,27–0,41 | ~4–6 | Qualidade superior, mas 4–30× mais caro; só se cliente exigir |
| Gemini 3.5 Flash | US$ 1,50 / US$ 9,00 | — | — | Padrão agêntico da Google (GA desde 19/05/2026) |
| Gemini 2.5 Flash-Lite | US$ 0,10 / US$ 0,40 | — | — | Preço idêntico ao antigo 2.0 Flash, mas aposenta em 16/10/2026 |

## Capacidade por investimento mensal

| Investimento | Modelo | Requisições/dia | Clientes/dia | Clientes/mês |
|---|---|---|---|---|
| US$ 50/mês | DeepSeek V4 Flash | ~2.000 chamadas LLM | ~130–200 | ~3.900 |
| US$ 50/mês | GPT-5 mini | ~550 chamadas | ~37–44 | ~1.100 |
| US$ 200/mês | DeepSeek V4 Flash | ~8.000 chamadas | ~520–800 | ~15.600 |

## Descontinuações relevantes (2026)

- **claude-sonnet-4**: parou de aceitar requisições em 15/06/2026. Sucessor: Claude Sonnet 5 (30/06/2026).
- **gemini-2.0-flash**: deprecado 18/02/2026, desligado 01/06/2026. Rota "mesmo preço": Gemini 2.5 Flash-Lite (até 16/10/2026); depois, o mais barato da Google é Gemini 3.1 Flash-Lite (US$ 0,25/1,50).
- **deepseek v3/r1**: retirados da API em 24/07/2026 (substituídos pela linha V4).

## Dificuldades esperadas

1. **Rate limits**: DeepSeek V4 Flash sem RPM; GPT-5 mini tem tiers de RPM/TPM que exigem upgrade progressivo.
2. **Latência**: loop agêntico sequencial (15 chamadas × 2–10 s) — exigir job queue (já existe: `job_timeout_s: 600`).
3. **Qualidade de tool calling em PT-BR**: DeepSeek/GPT-5 mini fortes; Claude só se justifica por exigência do cliente.
4. **Residência de dados**: dados de leads (e-mails nominais incidentais) trafegam para provedores estrangeiros — relevante sob LGPD (arts. 46–49) e para clientes corporativos.
5. **Custo de contexto longo**: considerar prompt caching para prompts de sistema + definições de ferramentas (DeepSeek e Anthropic têm cache; verificar plano do provedor escolhido).

## Limites de teste sugeridos (trial/MVP)

- 15 dias, **10 jobs totais**, máx. 30 chamadas LLM por job, 1 usuário.
- Crédito inicial ~US$ 10–20 (cobre ~800 jobs no DeepSeek V4 Flash).
- Alternativa de teste grátis: Gemini 3 Flash (tier free, ~1.500 RPD → ~100 jobs/dia teóricos) — **apenas como fallback/teste**, não produção com dados de clientes.

## Custo mensal do produto (sugestão de precificação)

- Custo direto por job: ~R$ 0,07–0,25 (câmbio ~R$ 5,50/US$).
- Sugestão: **R$ 149–299/mês por cliente** com cota de ~100 jobs/mês → margem bruta confortável (custo LLM ~R$ 7–25/cliente + Google Places US$ 0–60/mês + infra).
- Com US$ 50/mês de LLM é possível atender ~100–200 clientes leves/mês.

## Fontes (2026)

- curlscape.com/blog/google-gemini-api-pricing-guide-2026
- metacto.com/blogs/the-true-cost-of-google-gemini-a-guide-to-api-pricing-and-integration
- rapidevelopers.com/ai-api-limits-performance-matrix/claude-4-sonnet
- llmbill.app/models/anthropic/claude-sonnet-4
- langcopilot.com/claude-sonnet-4-token-calculator
- benchlm.ai (preço Sonnet 5)

> Valores marcados com estimativa (custo/job, capacidade/dia) dependem do volume real de tokens por job — validar com telemetria (LiteLLM registra uso por chamada).
