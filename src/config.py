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
    HEALTHCHECK_PORT: int
    TRANSLATOR_QUEUE: str

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


settings = Settings()
