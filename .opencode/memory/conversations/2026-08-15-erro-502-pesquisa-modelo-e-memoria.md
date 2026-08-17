# Conversa 2026-08-15 — Erro 502, pesquisa de modelos/API Google/legalidade e criação da memória

**Data:** 15/08/2026
**Participantes:** usuário + agente `onboarding` (opencode)
**Projeto:** scrapAI (prospecção B2B de leads — backend FastAPI + frontend React/Vite)

---

## 1. Diagnóstico do erro 502 (concluído — não corrigido)

**Sintoma:** requisições `/api/*` no frontend dev retornam 502 Bad Gateway.

**Causa raiz (confirmada com evidências):**
- O backend Uvicorn estava rodando em `127.0.0.1:8001`
  (`uvicorn app.main:app --reload --port 8001`).
- O proxy do Vite (`frontend/vite.config.ts`) encaminha `/api` para
  `http://127.0.0.1:8000`.
- Nada escutava na 8000 → conexão recusada → o proxy devolve 502.

**Evidências:** `ss -tlnp` (uvicorn em 8001, Vite em 5173/5174), `curl` na 8000
(HTTP 000/refused), 8001 (HTTP 200), e `/api/health` via 5173 e 5174 (502).
`.env` do backend define `PORT=8000`, mas o comando sobrescreveu com
`--port 8001`.

**Soluções possíveis (não executadas):**
1. Subir o backend na 8000: `uvicorn app.main:app --reload --port 8000`.
2. Alterar `vite.config.ts` target para `http://127.0.0.1:8001`.
3. Padronizar via `.env` (`PORT=8000`) sem `--port` fixo no comando.

**Observação:** duas instâncias do Vite ativas (5173 e 5174) — uma pode estar
obsoleta. Em produção (Dockerfile EXPOSE 8000), mesma causa se o mapeamento
de porta do host divergir do alvo do proxy.

---

## 2. Pesquisa — melhor modelo LLM pago (custo/benefício) — ago/2026

**Contexto do projeto:** loop agêntico de tool-calling (até 15 passos/job,
~60k tokens input + ~15k output por job estimados), LiteLLM, modelo atual
`gpt-4o-mini` (`backend/app/config.py: llm_model`).

**Recomendações finais:**

| Modelo | Preço (1M in/out) | Custo/job | Jobs/dia com US$ 50/mês |
|---|---|---|---|
| 🥇 **DeepSeek V4 Flash** | US$ 0,14 / US$ 0,28 | ~US$ 0,013 | ~130–200 |
| 🥈 **GPT-5 mini** | US$ 0,25 / US$ 2,00 | ~US$ 0,045 | ~37–44 |
| Claude Sonnet 5 (ref.) | US$ 3,00 / US$ 15,00 (promo US$ 2/10 até 31/08/2026) | ~US$ 0,27–0,41 | ~4–6 |

**Pontos-chave:**
- `claude-sonnet-4` e `gemini-2.0-flash` foram **descontinuados em 2026**
  (substitutos: Sonnet 5, Gemini 3.5 Flash / 2.5 Flash-Lite).
- DeepSeek V4 Flash: melhor tool-use multi-turn por dólar, contexto 1M, sem
  RPM, recomendado para produção de alto volume.
- GPT-5 mini: migração quase zero (mesma API OpenAI), ótimo fallback.
- Gemini 3 Flash grátis (tier free, ~1.500 RPD) serve para teste/MVP
  (~100 jobs/dia teóricos), mas não para produção com dados de clientes.
- Claude: só se o cliente exigir qualidade de instrução superior — não é o
  caso do scrapAI (trechos curtos estruturados).

**Limite de teste sugerido para o MVP:** 5–10 jobs/dia por conta trial,
~30 chamadas LLM por job, crédito inicial ~US$ 10–20.

---

## 3. Pesquisa — API Google para Google Business (ago/2026)

**Veredito:** integrar SIM, como **módulo de descoberta** (não como banco de
leads persistente).

- **GBP API (Google Business Profile):** grátis e ativa, mas **inútil para
  prospecção** — só gerencia perfis que você administra (exige perfil
  verificado há 60+ dias + aprovação manual). ❌ Não usar para descobrir leads.
- **Places API (New) — `places:searchText`:** ✅ a opção certa. Retorna nome,
  endereço, **telefone**, **website**, avaliações. **NÃO retorna e-mail** (em
  nenhum tier) — o e-mail continua vindo do scraping do site (core do scrapAI).
- **Preços (faixa 0–100 mil/mês):** Text Search Enterprise US$ 35/1.000
  (1.000 grátis/mês); Place Details Enterprise US$ 20/1.000; Essentials
  grátis/ilimitada (place_id). Crédito fixo de US$ 200/mês foi **aposentado
  em 01/03/2025** (viraram faixas grátis por SKU).
- **Custo estimado:** 1.000 empresas/mês ≈ **US$ 0–35/mês** (~R$ 0–210);
  5.000 ≈ US$ 140; 10.000 ≈ US$ 315. Orçamento MVP recomendado: US$ 0–60/mês
  com quota diária no Cloud Console.
- **Restrições (ToS):** proibido armazenar/cachear nome/telefone/website da
  API (só `place_id` pode ser persistido indefinidamente; lat/lng 30 dias);
  teto de **60 resultados por consulta** (exige fatiar cidade em tiles +
  deduplicar por place_id); **scraping do Google Maps é proibido** pelo ToS.
- **Pipeline sugerido:** Places (descobre telefone/website/segmento) →
  scrapAI (extrai e-mail/WhatsApp do site da empresa) → qualificação →
  cadência.

---

## 4. Pesquisa — Legalidade (LGPD, scraping, Google) — ago/2026

> Análise informativa de pesquisa — NÃO é aconselhamento jurídico formal.

**Veredito geral:** o **núcleo do modelo é viável** no Brasil (prospecção B2B
de dados públicos de empresas), com 3 pontos de atenção:

| Atividade | Risco |
|---|---|
| Dados de PJ (CNPJ/CNAE/cadastrais) | BAIXO (fora da LGPD) |
| Crawling de site oficial p/ e-mail/telefone institucionais (`contato@`) | BAIXO–MÉDIO (art. 7º, §4º LGPD) |
| E-mail nominal `nome.sobrenome@empresa` | MÉDIO (é dado pessoal; exige teste de legítimo interesse documentado) |
| Celular pessoal de sócios/funcionários | ALTO (não coletar) |
| **Vender dados pessoais como produto** ("base de decisores") | **ALTO** (caso Serasa; repetitivos STJ 2.226.946/2.226.097 pendentes) |
| Cold e-mail B2B corporativo com opt-out | BAIXO–MÉDIO (legítimo interesse art. 7º, IX) |
| WhatsApp/SMS em massa sem opt-in | ALTO (LGPD + banimento Meta + Resolução Anatel 632/2014) |
| Scraping do Google Maps | ALTO (proibido pelo ToS) |
| Places API (com respeito ao cache) | BAIXO (origem) / MÉDIO (armazenamento) |

**Compliance recomendado para o MVP:** política de privacidade (art. 9º),
LIA (teste de legítimo interesse) documentado + RAT, canal de direitos do
titular (art. 18, resposta em 15 dias), DPA com clientes (art. 39 — cliente
controlador, scrapAI operador), minimização (nunca CPF/celular pessoal),
logs por 6 meses (Marco Civil art. 15), respeito a robots.txt (risco art.
154-A CP ao burlar barreiras), opt-out funcional em todo e-mail.

**Nota:** MP 1.317/2025 + Lei 15.352/2026 renomearam a ANPD para "Agência
Nacional de Proteção de Dados".

---

## 5. Sistema de memória criado (esta conversa)

- Criado `.opencode/memory/` com `README.md`, `index.md` e
  `conversations/` (este arquivo).
- Criado `opencode.json` na raiz do projeto com
  `instructions: [".opencode/memory/index.md"]` (carrega o índice
  automaticamente em toda sessão).
- Instrução de comportamento MEMORY adicionada ao prompt do agente
  `onboarding` no `~/.config/opencode/opencode.jsonc` (ler índice no início,
  ler conversa relevante, escrever ao final).

## 6. Relatórios de pesquisa salvos no repositório (fim da sessão)

- `docs/research/README.md` — índice
- `docs/research/2026-08-15-modelo-llm-custo-beneficio.md` — ranking de modelos
- `docs/research/2026-08-15-google-places-api.md` — GBP × Places API + custos
- `docs/research/2026-08-15-legalidade-lgpd-scraping.md` — análise LGPD/ANPD/STJ

## 7. Teste: usar big-pickle (modelo do opencode) no scrapAI — ❌ NÃO É POSSÍVEL (15/08/2026)

Pergunta do usuário: "dá para usar o big-pickle como modelo do scrapAI?" Teste de conectividade realizado:

- `api.opencode.ai` (app/console): aceita a chave do `auth.json` (sem 401), mas **não expõe endpoints OpenAI-compatíveis** (`/v1/models`, `/models`, `/v1/chat/completions`, `/chat/completions` → "Not Found").
- `inference.opencode.ai`: host real de inferência, mas **protegido por Cloudflare Access (SSO)** — retorna página de login; a chave de API não autentica.
- `models.opencode.ai`: é o models.dev (catálogo público) — `big-pickle` **nem aparece** no catálogo (modelo interno/privado).
- Processo local do opencode (PID 28648) **não abre porta TCP** — inferência via cliente interno com sessão SSO.
- **Conclusão:** não há endpoint público consumível por um backend externo com a chave disponível. Manter a recomendação: APIs dedicadas (DeepSeek V4 Flash / GPT-5 mini) para produção. `big-pickle` fica como ferramenta de desenvolvimento.

---

## Decisões pendentes / próximos passos (para retomar em outra sessão)

1. **502:** escolher e aplicar uma das 3 correções de porta.
2. **Modelo LLM:** decidir se troca `gpt-4o-mini` → DeepSeek V4 Flash /
   GPT-5 mini (config em `backend/app/config.py` + `.env`).
3. **Google Places:** decidir se integra como módulo de descoberta
   (endpoint `places:searchText`, field mask, tiling, dedup por place_id,
   armazenar só place_id).
4. **Pricing do produto:** sugestão preliminar de R$ 149–299/mês por cliente
   (custo LLM ~US$ 0,01–0,05/job + Places US$ 0–60/mês + infra).
5. **Compliance:** implementar checklist LGPD (LIA, RAT, política de
   privacidade, DPA, opt-out).
