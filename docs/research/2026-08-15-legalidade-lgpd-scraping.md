# Pesquisa — Legalidade do modelo de negócio scrapAI (LGPD, scraping, cold outreach, ToS Google)

**Data:** 15/08/2026 · **Agente:** researcher · **Status:** pesquisa concluída
> ⚠️ **Análise informativa de pesquisa — NÃO constitui aconselhamento jurídico formal.**
> Contrate advogado especializado (LGPD) antes de decisões de negócio.

## Veredito geral

O **núcleo do modelo é juridicamente viável no Brasil**: prospecção B2B a partir de dados públicos de empresas (CNPJ/CNAE/cadastrais — fora da LGPD) + contato por canal comercial com identificação e opt-out (legítimo interesse, art. 7º, IX). Três pontos de maior atenção: dados pessoais incidentais, venda de dados pessoais como produto, e canais de contato em massa.

## 1. LGPD — o que é "dado pessoal" no acervo do scrapAI

| Dado | Enquadramento | Consequência |
|---|---|---|
| CNPJ, razão social, CNAE, endereço comercial, capital | **Não é dado pessoal** (PJ) | Fora da LGPD; uso livre com fonte pública (LAI 12.527/2011) |
| Telefone fixo institucional, site corporativo | Em regra, dado da empresa | Uso defensável; atenção se identifica pessoa física |
| E-mail genérico (`contato@`, `vendas@`) | Dado da empresa | Menor risco |
| **E-mail nominal (`joao.silva@empresa.com.br`)** | **É dado pessoal** (identifica pessoa natural) | LGPD integral: base legal, transparência, direitos do titular |
| CPF, celular pessoal, endereço residencial de sócios | **É dado pessoal** | **NÃO coletar** para prospecção |

### Bases legais (correção técnica importante)
- **Não existe** "art. 7º, VI para dados publicados" — o art. 7º, VI é exercício de direitos em processo. Dados publicados pelo titular = **art. 7º, §4º** (com boa-fé/finalidade do §3º).
- **Legítimo interesse (art. 7º, IX c/c art. 10)** é a base recomendada para cold outreach B2B. Exige **teste de balanceamento (LIA) documentado** em 3 fases — finalidade legítima e específica; necessidade (mínimo de dados); balanceamento (expectativa razoável, salvaguardas) — conforme Guia Orientativo ANPD "Legítimo Interesse" (jan/2024).
- **Consentimento** não é a base adequada para B2B (só B2C promocional, WhatsApp/SMS, cookies).
- **LGPD não exige aviso prévio** antes do 1º contato B2B (diferente do GDPR/CNIL), mas exige identificação, finalidade e **opt-out funcional** respeitado imediatamente (art. 18, §2º) — a falha mais sancionada pela ANPD (Telekall 2023, INSS 2024, RaiaDrogasil 2025).

### Operador × controlador no SaaS
- Na coleta/pontuação própria: scrapAI decide finalidade → atua como **controlador** (possivelmente conjunto).
- No uso pelo cliente: cliente define finalidade, scrapAI executa → **operador**; responderá **solidariamente** se descumprir LGPD (art. 42, §1º, I). **DPA (art. 39) com cada cliente é indispensável.**

## 2. Scraping de dados públicos

- **Não é ilegal per se no Brasil**, mas a ANPD considera web scraping **tratamento de dados** sujeito à LGPD (Radar Tecnológico nº 3, nov/2024), mesmo para dados publicados voluntariamente.
- **Agenda Regulatória 2025-2026** (Res. 31/2025): data brokers são prioridade; **Mapa 2026-2027** (Res. 30/2025): IA e coleta em escala são foco de fiscalização.
- **CNIL (jan/2026)**: scraping de dados públicos é em regra legítimo interesse, com salvaguardas — respeitar robots.txt/CAPTCHA, excluir dados sensíveis, minimização, deletar incidentais.
- **LinkedIn v. hiQ (EUA)**: raspar dados abertos não é crime no CFAA — **relevância limitada ao Brasil** (temos LGPD; art. 154-A do CP pune burlar barreiras técnicas).
- **Marco Civil (12.965/2014)**: art. 11 (aplicação da lei BR a qualquer tratamento no território), art. 7º VIII/IX (informação e consentimento), **art. 15 (guardar registros de acesso por 6 meses)**.
- **Jurisprudência**: TJDFT 2022 (dados cadastrais não autorizam segmentação sem transparência); ACP Serasa 2021 (suspensão de venda de listas); STJ REsp 1.758.799-MG (dano moral presumido por comercialização sem comunicação); REsp 2.201.694/SP (set/2025, dano moral presumido); **REsps 2.226.946/2.226.097 afetados ao rito dos repetitivos (2026)** — podem redefinir o mercado de leads.

## 3. E-mail marketing / cold outreach B2B

- **Decreto 10.610/2020 não existe** (o Decreto 10.610/2021 é o PGMU de telecomunicações). Não há decreto regulamentando e-mail marketing na LGPD.
- **Cold e-mail B2B corporativo é legal sob legítimo interesse** (consenso de escritórios), com: e-mail corporativo (nunca Gmail pessoal), oferta relevante ao CNAE, identificação completa, **opt-out funcional**, LIA + RAT + prova da origem dos dados.
- **CDC art. 43** + Lei 12.414/2011: cadastros exigem comunicação prévia — ausência gera dano moral presumido (STJ).
- **Anatel Res. 632/2014**: mensagens publicitárias exigem consentimento prévio (art. 3º, XVIII); chamadas só em horário comercial e volume razoável (art. 43); disparos massivos = uso inadequado da rede (art. 44). "Não Me Perturbe" (adesão obrigatória desde set/2025).
- **WhatsApp Business (2026)**: exige opt-in por categoria; spam → sanções progressivas → **banimento definitivo** (risco duplo: LGPD + perda do canal).

## 4. API oficial Google × scraping do Google Maps

- **Scraping do Google Maps: proibido** pelo ToS ("no scraping"); risco contratual e de desligamento. O Google Maps não é fonte "aberta".
- **API oficial (Places/Business Profile): origem licenciada (menor risco)** — MAS o ToS **proíbe pré-buscar, cachear ou armazenar** o conteúdo além de `place_id` (indefinido) e lat/lng (30 dias). Armazenar payloads da API no PostgreSQL **viola o ToS**.
- **Desenho compatível:** armazenar só `place_id` + dados de PJ (CNPJ); re-consultar sob demanda; não agregar/comercializar conteúdo do Google como produto.
- LGPD permanece aplicável aos dados pessoais incidentais nas respostas da API.

## 5. Recomendações de compliance para o MVP

1. Política de privacidade e aviso de transparência (art. 9º): fontes, finalidade, base legal, compartilhamentos, direitos.
2. **LIA documentado** (finalidade/necessidade/balanceamento, modelo Guia ANPD) + **RAT** (art. 37) com origem de cada dado (URL, data, base legal).
3. **Canal de direitos do titular (art. 18)**: acesso, correção, anonimização/bloqueio/eliminação, oposição; resposta em 15 dias (art. 19, II); **respeito imediato a opt-outs**.
4. **Minimização**: nunca CPF, dados sensíveis, celulares/e-mails pessoais de sócios fora de contexto comercial público.
5. **DPA com cada cliente SaaS** (art. 39): papéis, finalidade limitada, proibição de revenda, retenção, segurança, exclusão ao fim.
6. **Não vender dados pessoais como produto** — o produto deve ser ferramenta de prospecção de empresas (dados de PJ).
7. Logs e rastreabilidade (fonte/URL/data/base legal de cada coleta; guarda de 6 meses — Marco Civil art. 15).
8. Segurança (arts. 46–49): criptografia, controle de acesso, retenção; comunicação de incidentes à ANPD (art. 48).
9. Anonimização/agregação para pontuação e analytics (art. 12) — reduz superfície LGPD.
10. Encarregado/DPO: mitigante expresso na dosimetria de sanções (art. 52, §1º, IX). ME/startup: Res. ANPD 2/2022 (pequeno porte) dispensa encarregado com canal de comunicação — mas **não isenta** bases legais/princípios; recomenda-se assumir o padrão pleno.
11. **Scraping disciplinado**: respeitar robots.txt; não burlar bloqueios (art. 154-A CP); não raspar áreas autenticadas; não usar dados de plataformas que proíbem scraping (LinkedIn/Instagram) como produto; excluir dados sensíveis incidentais.
12. API Google: respeitar políticas de cache (place_id persistente; demais sob demanda ou máx. 30 dias).

## Resumo de risco por atividade

| Atividade | Risco |
|---|---|
| Buscar/filtrar empresas por CNPJ/CNAE (RFB/Dados Abertos) | 🟢 BAIXO |
| Crawling do site oficial p/ e-mail/telefone institucionais | 🟢 BAIXO–MÉDIO (risco se ToS/robots.txt proibirem) |
| Extrair/armazenar e-mail nominal e nome de funcionários | 🟡 MÉDIO (exige LIA + transparência) |
| Celular pessoal de sócios/funcionários | 🔴 ALTO — não coletar |
| Pontuação/ranqueamento e armazenamento | 🟡 MÉDIO (decisão automatizada — art. 20) |
| **Vender dados pessoais de terceiros como produto** | 🔴 **ALTO** (Serasa/TJDFT + repetitivos STJ 2.226.946/2.226.097) |
| Cold e-mail B2B corporativo com opt-out | 🟢 BAIXO–MÉDIO (art. 7º, IX) |
| Telemarketing em massa | 🟡–🔴 MÉDIO–ALTO (Anatel 632/2014, Não Me Perturbe) |
| WhatsApp/SMS em massa sem opt-in | 🔴 ALTO (LGPD + Meta + Anatel) |
| API Google Places/Business Profile | 🟢 BAIXO (origem) / 🟡 MÉDIO (armazenamento) |
| Scraping do Google Maps | 🔴 ALTO (proibido no ToS) |
| SaaS para clientes (modelo operador) | 🟡 MÉDIO (exige DPA + segregação de papéis) |

## Notas legislativas 2025–2026

- **MP 1.317/2025 + Lei 15.352/2026**: ANPD renomeada para **"Agência Nacional de Proteção de Dados"**.
- **EC 115/2022**: proteção de dados como direito fundamental (art. 5º, LXXIX).

## Fontes principais

- Legislação: LGPD (13.709/2018 c/c MP 1.317/2025, Lei 15.352/2026); Marco Civil (12.965/2014, arts. 7º, 10, 11, 15, 19); CDC (8.078/1990, art. 43); Lei 12.414/2011 (LC 166/2019); Decreto 11.034/2022 (SAC); Res. Anatel 632/2014 (arts. 3º-XVIII, 43, 44).
- ANPD: Guia "Legítimo Interesse" (jan/2024); Guia de Agentes de Tratamento (2021); Radar Tecnológico nº 3 (nov/2024); Res. 2/2022 (pequeno porte); Res. 4/2023 (dosimetria); Res. 23/2024 e 31/2025 (agenda 2025-2026); Res. 30/2025 (mapa 2026-2027); sanções Telekall/INSS/SEEDF/MS/RaiaDrogasil.
- STJ: REsp 1.758.799-MG; REsp 1.660.168-RJ; REsp 2.115.461/SP e 2.133.261/SP (2024); REsp 2.147.374/SP (2024); REsp 2.135.783/SP (2024, perfilização); REsp 2.201.694/SP (2025); REsps 2.226.946/2.226.097 (repetitivos 2026).
- STF: RE 1.010.606/RJ (2021). TJDFT: Ap. Cível 0736634-81.2020.8.07.0001 (2022); ACP Serasa (2021).
- Anatel: Res. 632/2014; PGMU; "Não Me Perturbe" (set/2025); Origem Verificada (2025).
- Google: Places API Policies; Maps Platform ToS + Service-Specific Terms; Business Profile APIs Policies (2025).
- Meta: WhatsApp Business Terms; Política de Mensagens (2026).
- Internacional: CNIL focus sheet web scraping (jan/2026); EDPB Opinion 28/2024 e orientação final (jul/2026); hiQ v. LinkedIn (9th Cir., 2022).
- Doutrina/prática: eesier, Prospecta, LeadCNPJ, Disparo em Massa, CNPJ Data, LegalSuite, Assis e Mendes, Calabria & Villa Gonzalez, Machado Meyer, oHub/Base, Clifford Chance.
