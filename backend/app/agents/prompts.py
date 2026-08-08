from __future__ import annotations

SYSTEM_PROMPT = """Você é o assistente de prospecção de leads da plataforma scrapAI.

Regras obrigatórias:
1. Comece SEMPRE com uma chamada a search_web para descobrir candidatos.
2. Prefira sites oficiais das empresas; evite agregadores e redes sociais como primeira fonte.
3. Para cada candidato promissor, chame crawl_url para ler o conteúdo da página.
4. Depois de ler a página, chame extract_contacts para extrair os contatos do candidato.
5. Se extract_contacts não retornar contatos, repita com js_rerun=true para carregar conteúdo dinâmico.
6. Reúna até max_leads leads, respeitando o limite de max_pages de páginas visitadas.
7. Ao final, chame finalize_results UMA ÚNICA VEZ, com TODOS os leads coletados e um resumo em português (PT-BR).
8. O campo confidence deve estar entre 0 e 1, refletindo quantidade e qualidade dos contatos encontrados.
9. NUNCA invente contatos, nomes, sites ou URLs. Se não encontrar contato, envie o lead com confidence baixa e uma nota explicando.
10. Responda apenas em português do Brasil."""

TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Busca na web por empresas/candidatos a lead usando uma consulta de texto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Consulta de busca.",
                    },
                    "max_results": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crawl_url",
            "description": "Acessa uma URL e retorna o texto da página (título e trecho).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL da página a acessar.",
                    },
                    "js": {
                        "type": "boolean",
                        "default": False,
                        "description": "Executar JavaScript para carregar conteúdo dinâmico.",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract_contacts",
            "description": "Extrai contatos (e-mail, telefone, WhatsApp, redes sociais) da página de um candidato.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL da página do candidato.",
                    },
                    "js_rerun": {
                        "type": "boolean",
                        "default": False,
                        "description": "Recarregar a página com JavaScript se não houver contatos.",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finalize_results",
            "description": "Finaliza a prospecção enviando todos os leads coletados e um resumo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Resumo da prospecção em PT-BR.",
                    },
                    "leads": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "segment": {"type": "string"},
                                "city": {"type": "string"},
                                "state": {"type": "string"},
                                "website": {"type": "string"},
                                "emails": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "phones": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "whatsapp": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "social": {
                                    "type": "object",
                                    "additionalProperties": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "null"},
                                        ]
                                    },
                                },
                                "source_url": {"type": "string"},
                                "confidence": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "notes": {"type": "string"},
                            },
                            "required": ["name", "source_url"],
                        },
                    },
                },
                "required": ["summary", "leads"],
            },
        },
    },
]

AUTO_FINALIZE_PROMPT = (
    "Você deve chamar finalize_results agora, com todos os leads coletados até o "
    "momento (mesmo que nenhum), incluindo um resumo em português (PT-BR)."
)
