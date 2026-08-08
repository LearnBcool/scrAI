from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    app_name: str = "scrapAI"
    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000

    # PostgreSQL connection (psycopg 3). Required at runtime; empty default
    # fails fast with a clear error when DATABASE_URL is not provided.
    database_url: str = ""

    # CORS: comma-separated list of allowed origins.
    cors_origins: str = "http://localhost:5173"

    # LLM provider (OpenAI-compatible via LiteLLM)
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str | None = None
    llm_api_base: str | None = None

    # Search provider: duckduckgo (default) | tavily | serpapi
    search_provider: str = "duckduckgo"
    tavily_api_key: str | None = None
    serpapi_api_key: str | None = None

    # Vector memory (optional RAG)
    vector_db_enabled: bool = False
    chroma_dir: str = "./data/chroma"

    # Crawling
    crawl_max_pages: int = 20
    crawl_concurrency: int = 2
    crawl_page_timeout_ms: int = 15000
    crawl_domain_delay_s: float = 1.0

    # Jobs / agent loop
    job_timeout_s: int = 600
    max_tool_steps: int = 15

    # Data storage
    data_dir: str = "./data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
