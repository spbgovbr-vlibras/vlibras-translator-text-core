import os
from enum import Enum
from typing import Any

from pydantic import AmqpDsn, BaseSettings, validator


class ModeEnum(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"
    HOMOLOG = "HOMOLOG"
    TESTING = "TESTING"


class Settings(BaseSettings):
    MODE: ModeEnum = ModeEnum.DEVELOPMENT

    ENABLE_DL_TRANSLATION: bool = True
    HEALTHCHECK_PORT: int
    TRANSLATOR_QUEUE: str

    AMQP_HOST: str
    AMQP_USER: str
    AMQP_PASS: str
    AMQP_PORT: str | int = 5672
    AMQP_PREFETCH_COUNT: int = 1
    AMQP_HEART_BEAT: int = 60
    AMQP_URI: AmqpDsn | None

    @validator("AMQP_URI", pre=True)
    def assemble_rabbit_connection(
        cls, v: str | None, values: dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        return AmqpDsn.build(
            scheme='amqp',
            host=values.get("AMQP_HOST"),
            password=values.get("AMQP_PASS"),
            user=values.get("AMQP_USER"),
            port=values.get("AMQP_PORT"),
        )

    class Config:
        case_sensitive = True
        env_file = os.path.expanduser(".env")


settings = Settings()
