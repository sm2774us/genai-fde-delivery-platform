"""Centralized, versioned configuration — mirrors how an FDE pod manages
per-client environment config across dev/stage/prod without code changes."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    log_level: str = "INFO"

    llm_provider: str = "mock"  # mock | anthropic | azure_openai | bedrock | vertex
    anthropic_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""

    cloud_provider: str = "aws"  # aws | azure | gcp
    vector_store: str = "inmemory"  # inmemory | pgvector | opensearch

    # Quality gates enforced by the CI-integrated eval harness (app/eval/harness.py)
    quality_gate_min_score: float = 0.8
    hallucination_max_rate: float = 0.05
    latency_p95_ms_budget: int = 4000
    cost_per_query_budget_usd: float = 0.05
    hitl_required_action_risk: str = "high"


@lru_cache
def get_settings() -> Settings:
    return Settings()
