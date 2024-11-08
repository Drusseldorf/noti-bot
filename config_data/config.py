from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

ENV_FILE = Path(__file__).parent.parent.joinpath(".env")


class Settings(BaseSettings):
    bot_token: str
    db_url: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding="utf-8", env_nested_delimiter="__"
    )


settings = Settings()
