import os
from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


def _current_environment() -> Environment:
    return Environment(os.getenv("APP_ENV", Environment.DEV.value))


class Secrets(BaseSettings):
    """
    Typed access to credentials, loaded from the `secrets/.env.<APP_ENV>`
    file matching the current environment (defaults to `dev`).
    """

    environment: Environment = Field(default_factory=_current_environment)

    model_config = SettingsConfigDict(
        env_file=f"secrets/.env.{_current_environment().value}",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True,
    )


@lru_cache
def get_secrets() -> Secrets:
    """Returns the process-wide `Secrets` instance, loaded once and cached."""
    return Secrets()


secrets = get_secrets()
