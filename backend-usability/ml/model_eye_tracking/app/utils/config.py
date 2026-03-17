import os
from typing import Literal, Optional

import torch
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 9000
    workers_count: int = Field(default=1, ge=1)

    # ML Модель
    model_device: Literal["cpu", "cuda", "mps"] = "cuda"
    model_workers: int = Field(default=2, ge=1)
    model_worker_type: Literal["thread", "process"] = "process"

    # Препроцессинг
    preprocessing_workers: int = Field(default=4, ge=1)
    preprocessing_timeout: int = 30

    # Логирование
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_file: Optional[str] = "eyetracking.log"

    # Асинхронность
    request_timeout: int = 60
    max_queue_size: int = 100

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../..", ".env")),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("model_device")
    def validate_device(cls, v):
        if v == "cuda" and not torch.cuda.is_available():
            return "cpu"
        if v == "mps" and not torch.backends.mps.is_available():
            return "cpu"
        return v


settings = Settings()