import pathlib

from pydantic import Extra
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_API: str = "/api/v1"

class Settings(BaseSettings):
    MODE: str
    SQL_PATH: str
    ASYNC_ENGINE: str
    SYNC_ENGINE: str
    SECRET_KEY: str
    ALGORITHM: str

    @property
    def DATABASE_URL_async(self) -> str:
        return f"{self.ASYNC_ENGINE}:{self.SQL_PATH}"

    @property
    def DATABASE_URL_sync(self) -> str:
        return f"{self.SYNC_ENGINE}:{self.SQL_PATH}"


    model_config = SettingsConfigDict(
        env_file=f"{pathlib.Path(__file__).resolve().parent.parent.parent}/.env",
        extra="allow"
    )

settings = Settings()