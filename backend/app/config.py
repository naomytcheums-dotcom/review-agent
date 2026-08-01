from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./review_agent.db"

    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = ""

    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str = ""

    cors_origins: list[str] = ["http://localhost:5173"]

    site_password: str = ""


settings = Settings()
