import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = Field(title="", default="localhost")
    DB_PORT: int = Field(title="", default=5432)
    DB_USERNAME: str = Field(title="")
    DB_PASSWORD: str = Field(title="")
    DB_NAME: str = Field(title="")
    DB_POOL_SIZE: int = Field(title="", default=5)
    DB_MAX_OVERFLOW: int = Field(title="", default=5)
    DB_ADMIN_MAIL: str = None
    DB_ADMIN_PASSWORD: str = None

    @property
    def get_url_database(self) -> str:
        """Собирает асинхронный URL для подключения к PostgreSQL."""
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USERNAME}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    class Config:
        env_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", ".env"
            )
        )
        env_file_encoding = "utf-8"

settings = Settings()
print(settings)