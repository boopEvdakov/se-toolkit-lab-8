"""Settings for the observability MCP server."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Observability service settings."""

    victorialogs_url: str = "http://localhost:42010"
    victoriatraces_url: str = "http://localhost:42011"

    class Config:
        env_prefix = "NANOBOT_"


def resolve_settings() -> Settings:
    """Resolve settings from environment or defaults."""
    return Settings()
