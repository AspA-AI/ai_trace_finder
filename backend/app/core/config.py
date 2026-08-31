from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./people_investigation.db"
    tavily_api_key: str | None = None
    github_token: str | None = None
    openai_api_key: str | None = None
    openai_extraction_model: str = "gpt-4o-mini"
    firecrawl_api_key: str | None = None
    tavily_base_url: str = "https://api.tavily.com"
    github_api_url: str = "https://api.github.com"
    request_timeout_seconds: float = 20.0
    provider_retry_attempts: int = 2
    max_search_rounds: int = 2
    max_queries_per_round: int = 5
    max_results_per_query: int = 10
    source_cache_ttl_hours: int = 24
    max_semantic_comparisons: int = 10

    # Keep secrets with the backend and make loading independent of cwd.
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
