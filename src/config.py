import os
from enum import Enum
from typing import Any

from pydantic import AmqpDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModeEnum(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"
    HOMOLOG = "HOMOLOG"
    TESTING = "TESTING"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=os.path.expanduser(".env"),
    )

    MODE: ModeEnum = ModeEnum.DEVELOPMENT

    ENABLE_DL_TRANSLATION: bool = True
    ENABLE_AGENT_GLOSS_REFINEMENT: bool = False
    HEALTHCHECK_PORT: int
    TRANSLATOR_QUEUE: str
    WORKER_CAPABILITIES_QUEUE: str
    GLOSS_REFINEMENT_QUEUE: str | None = None

    AGENT_PROVIDER: str | None = None
    AGENT_API_URL: str | None = None
    AGENT_API_KEY: str | None = None
    AGENT_MODEL: str | None = None

    AMQP_HOST: str
    AMQP_USER: str
    AMQP_PASS: str
    AMQP_PORT: str | int
    AMQP_PREFETCH_COUNT: int = 1
    AMQP_HEART_BEAT: int = 60
    AMQP_URI: AmqpDsn | None = None

    @model_validator(mode="before")
    @classmethod
    def assemble_rabbit_connection(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        if isinstance(values.get("AMQP_URI"), str):
            return values
        if not all(
            values.get(field)
            for field in ("AMQP_HOST", "AMQP_USER", "AMQP_PASS", "AMQP_PORT")
        ):
            return values

        values["AMQP_URI"] = AmqpDsn.build(
            scheme="amqp",
            host=values.get("AMQP_HOST"),
            password=values.get("AMQP_PASS"),
            username=values.get("AMQP_USER"),
            port=int(values.get("AMQP_PORT")) if values.get("AMQP_PORT") else None,
        )
        return values

    @model_validator(mode="after")
    def validate_agent_gloss_refinement_settings(self) -> "Settings":
        if not self.ENABLE_AGENT_GLOSS_REFINEMENT:
            return self

        if not self.GLOSS_REFINEMENT_QUEUE:
            raise ValueError(
                "GLOSS_REFINEMENT_QUEUE is required when "
                "ENABLE_AGENT_GLOSS_REFINEMENT is enabled."
            )

        if self.AGENT_PROVIDER not in {"openai", "ollama"}:
            raise ValueError(
                "AGENT_PROVIDER must be either 'openai' or 'ollama' when "
                "ENABLE_AGENT_GLOSS_REFINEMENT is enabled."
            )

        if not self.AGENT_API_URL:
            raise ValueError(
                "AGENT_API_URL is required when "
                "ENABLE_AGENT_GLOSS_REFINEMENT is enabled."
            )

        if not self.AGENT_API_KEY:
            raise ValueError(
                "AGENT_API_KEY is required when "
                "ENABLE_AGENT_GLOSS_REFINEMENT is enabled."
            )

        return self


settings = Settings()
