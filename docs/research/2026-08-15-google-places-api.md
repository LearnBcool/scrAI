# Pesquisa — APIs Google para prospecção de leads (Google Business)

**Data:** 15/08/2026 · **Agente:** researcher · **Status:** pesquisa concluída
**Legenda:** ✅ FATO 2026 (fonte oficial/múltiplas) · 🔶 Estimativa

## Veredito

Integrar **sim**, como **módulo de descoberta** (não como banco de leads persistente).
A **GBP API não serve** para prospecção; a **Places API (New) — Text Search** é a opção correta e complementar ao scraping de sites (que é o core do scrapAI).

## 1. Google Business Profile API (GBP API) — ❌ não usar p/ prospecção

- ✅ Ativa e mantida em 2026 (`developers.google.com/my-business`, changelog atualizado abr/2026).
- Gerencia perfis **dos quais você é dono/gestor** (avaliações, posts, verificação, métricas). **Não existe endpoint de busca/descoberta**.
- Requisitos: conta Google + projeto Cloud, Organization account no GBP, perfil **verificado há 60+ dias**, aprovação manual (sem aprovação: 0 QPM; aprovado: 300 QPM).
- **Preço: grátis**.
- Deprecações: Q&A API desligada em 03/11/2025 (substituída por "Ask Maps"/Gemini); demais endpoints ativos.

## 2. Places API (New) — ✅ a opção certa

### Endpoints relevantes

| Endpoint | Uso |
|---|---|
| `places:searchText` | Empresas por texto ("advogados em Curitiba") — todos os campos na resposta |
| `places:searchNearby` | Empresas num raio (máx. 50.000 m) |
| `places/{id}` (Place Details) | Detalhes de um place já conhecido |

### Campos × tier de preço

| Campo | Tier (Text Search) | Tier (Place Details) |
|---|---|---|
| `id` (place ID) | Essentials — grátis/ilimitado | Essentials — grátis |
| `displayName`, `businessStatus` | Pro | Pro (nome) / Pro |
| `formattedAddress`, `location`, `types` | Pro | Essentials |
| `nationalPhoneNumber`, `internationalPhoneNumber` | **Enterprise** | **Enterprise** |
| `websiteUri` | **Enterprise** | **Enterprise** |
| `rating`, `userRatingCount` | Enterprise | Enterprise |
| `reviews` (textos) | Enterprise + Atmosphere | Enterprise + Atmosphere |
| **E-mail** | ❌ **não existe em nenhum tier** | ❌ |

⚠️ O billing usa o **tier mais alto entre os campos solicitados** (field mask). Pedir telefone/website → Text Search Enterprise.

### Preços oficiais (faixa 0–100 mil/mês, página atualizada 11/08/2026)

| SKU | Faixa grátis/mês | US$ / 1.000 |
|---|---|---|
| Text Search Pro | 5.000 | $32,00 |
| Text Search Enterprise | 1.000 | **$35,00** |
| Text Search Enterprise + Atmosphere | 1.000 | $40,00 |
| Text Search Essentials (IDs only) | ilimitada | $0 |
| Place Details Essentials | 10.000 | $5,00 |
| Place Details Pro | 5.000 | $17,00 |
| Place Details Enterprise | 1.000 | $20,00 |
| Geocoding | 10.000 | $5,00 |

- ✅ O crédito fixo de **US$ 200/mês foi aposentado em 01/03/2025** — viraram faixas grátis por SKU.

### Estimativa de custo (1.000 empresas/mês, Text Search Enterprise)

| Cenário | Chamadas/mês | Custo US$ | Custo 🔶 R$ (~5,5–6,0) |
|---|---|---|---|
| **Enxuto (recomendado)** — field mask disciplinado + dedup por tile | 500–2.000 | **$0–35** | R$ 0–210 |
| 5.000 empresas (tiling com overhead 2×) | ~15.000 | ~$140 | R$ 770–840 |
| 10.000 empresas | ~30.000 | ~$315 | R$ 1.730–1.890 |

**Orçamento MVP recomendado: US$ 0–60/mês (~R$ 0–360)**, com **quota diária** configurada no Cloud Console (trava de gasto).

## 3. Restrições técnicas e de ToS

- **Teto de 60 resultados/consulta** (20/página × 3) → fatiar a cidade em tiles (raio 3–8 km) + deduplicar por `place_id`.
- `nextPageToken` válido após ~2–5 s (retry com backoff). Rate limit default ~6.000 QPM/método/projeto 🔶.
- **Scraping do Google Maps é proibido** pelo ToS ("export, extract, or otherwise scrape Google Maps Content") — risco de bloqueio/banimento de conta.
- **Cache/armazenamento**: `place_id` ✅ persistível indefinidamente; lat/lng ⚠️ até 30 dias; nome/endereço/telefone/website/avaliações ❌ não podem ser pré-buscados, indexados ou armazenados.
- **Atribuição** "Google Maps" obrigatória onde dados de Places forem exibidos.

## 4. Recomendação prática

1. **API:** Places (New) — `places:searchText` com `locationRestriction`/`locationBias`. Field mask Enterprise recomendada: `places.id, displayName, formattedAddress, nationalPhoneNumber, internationalPhoneNumber, websiteUri, businessStatus, types` (+ `rating`/`userRatingCount` se quiser qualificar). Evitar `reviews`, `openingHours` completos e `*`.
2. **Volume:** tiles por cidade + paginação (60) + dedup por `place_id`; refazer por campanha (sem armazenar payloads).
3. **Pipeline:** Places (descobre telefone/website/segmento) → scrapAI (site da empresa → e-mail/WhatsApp) → qualificação → cadência.
4. **Conformidade:** persistir só `place_id`; atribuição; não montar base permanente com payloads da API.
5. **Não usar:** GBP API (inútil p/ descoberta) e scraping do Google Maps (viola ToS).

## Fontes (2026)

- Preços oficiais: developers.google.com/maps/billing-and-pricing/pricing
- Usage/billing e tiers: developers.google.com/maps/documentation/places/web-service/usage-and-billing
- Campos por tier: developers.google.com/maps/documentation/places/web-service/data-fields
- Text Search (New): developers.google.com/maps/documentation/places/web-service/text-search
- Políticas/cache: developers.google.com/maps/documentation/places/web-service/policies
- ToS: cloud.google.com/maps-platform/terms · cloud.google.com/maps-platform/terms/maps-service-terms (§5.4 Caching)
- GBP API: developers.google.com/my-business/content/prereqs · /pricing · /sunset-dates
- Secundárias: slashpost.ai (11/05/2026) · openplacesapi.com/blog/google-places-api-pricing · woosmap.com/blog/google-places-api-pricing · bizcollect.dev (07/2026) · mapsleads.co · apify.com/blog/google-places-api-limits
