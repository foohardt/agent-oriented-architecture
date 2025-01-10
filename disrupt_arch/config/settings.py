from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env"), env_ignore_empty=True)

    OAI_API_KEY: str


settings = Settings()
