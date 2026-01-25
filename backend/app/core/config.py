"""
Application configuration using pydantic-settings.

Key pattern: Settings are loaded from environment variables automatically.
The `model_config` with `env_file` tells Pydantic to also check .env files.

Usage anywhere in the app:
    from app.core.config import settings
    print(settings.OPENROUTER_API_KEY)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic-settings automatically:
    - Reads from environment variables (case-insensitive)
    - Falls back to .env file if specified
    - Validates types and provides defaults
    """

    # OpenRouter configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "anthropic/claude-sonnet-4-20250514"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Opik observability
    OPIK_API_KEY: str = ""
    OPIK_PROJECT_NAME: str = "spendlens"

    # Database
    DATABASE_URL: str = "sqlite:///./spendlens.db"

    # App settings
    DEBUG: bool = False

    # LLM settings
    CATEGORIZATION_BATCH_SIZE: int = 10  # How many transactions to categorize per LLM call
    LOW_CONFIDENCE_THRESHOLD: float = 0.7  # Below this = flag for review

    # Valid categories - single source of truth
    VALID_CATEGORIES: list[str] = [
        "housing", "utilities", "groceries", "dining", "transportation",
        "shopping", "entertainment", "health", "personal_care", "subscriptions",
        "travel", "education", "financial", "income", "other"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # DATABASE_URL or database_url both work
        extra="ignore"  # Ignore extra env vars that aren't defined here
    )


# Singleton instance - import this everywhere
settings = Settings()
