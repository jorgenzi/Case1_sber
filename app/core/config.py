from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/bank_docs"
    max_file_size_mb: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()