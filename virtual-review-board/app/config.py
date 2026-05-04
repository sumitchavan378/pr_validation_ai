"""Application configuration loaded from environment."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    github_token: str = Field(..., alias="GITHUB_TOKEN")
    github_app_name: str = Field(default="VirtualReviewBoard", alias="GITHUB_APP_NAME")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    readiness_total_checks: int = Field(default=20, alias="READINESS_TOTAL_CHECKS")
    high_issue_yellow_threshold: int = Field(default=3, alias="HIGH_ISSUE_YELLOW_THRESHOLD")
    max_diff_chars: int = Field(default=120_000, alias="MAX_DIFF_CHARS")
    max_file_content_chars: int = Field(default=80_000, alias="MAX_FILE_CONTENT_CHARS")
    enable_github_check_run: bool = Field(default=True, alias="ENABLE_GITHUB_CHECK_RUN")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
