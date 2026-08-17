# Memória de Conversas — scrapAI

Sistema de memória persistente do projeto para que o agente do opencode
(agente `onboarding`) lembre o contexto entre conversas, sem que você precise
re-explicar o projeto ou decisões anteriores.

## Estrutura

```
.opencode/memory/
├── README.md              <- este arquivo (explica o sistema)
├── index.md               <- índice de uma linha por conversa (sempre atual)
└── conversations/
    └── YYYY-MM-DD-tema.md <- arquivo completo de cada conversa relevante
```

## Como funciona

1. **Início de conversa**: o agente lê `index.md` (carregado automaticamente
   via `instructions` no `opencode.json` do projeto — ver seção "Integração
   com o opencode" abaixo). Se o assunto atual for relacionado a uma conversa
   passada, ele lê o arquivo correspondente em `conversations/` antes de agir.

2. **Fim de conversa relevante**: quando a conversa produz decisões,
   arquitetura, resultados de pesquisa ou diagnósticos, o agente cria/atualiza
   um arquivo em `conversations/` e adiciona uma linha resumida em `index.md`.

3. **Regras de escrita**:
   - Arquivos concisos, em PT-BR, focados no que evita re-explicação.
   - Nome do arquivo: `YYYY-MM-DD-tema-resumido.md`.
   - Sempre atualizar o `index.md` junto (data, tema, 1 linha, link do arquivo).
   - Não guardar segredos (API keys, senhas) — apenas referências a `.env`.

## Integração com o opencode

O projeto possui `opencode.json` na raiz com:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [".opencode/memory/index.md"]
}
```

Isso faz o `index.md` ser carregado automaticamente no contexto de toda
sessão iniciada dentro deste projeto. O comportamento "ler conversa relevante"
e "escrever ao final" é instruído no prompt do agente `onboarding` no config
global (`~/.config/opencode/opencode.jsonc`), seção `MEMORY`.

## Manutenção

- Se uma conversa não agregar contexto (ex.: papo rápido), não criar arquivo.
- Se o índice crescer demais (> ~40 linhas), consolidar conversas antigas em
  um único arquivo `conversations/2026-resumo.md` e reduzir o índice.
- Apagar arquivos de conversa antigos que não têm mais valor é permitido,
  desde que o `index.md` seja atualizado em seguida.
