from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CyberTwin-RX"
    PHASE: str = "Phase 6 - Integrated Hackathon MVP"
    DATABASE_URL: str = "sqlite:///./cybertwin.db"


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
