from pydantic import BaseModel
import os

class Settings(BaseModel):
    API_NAME: str = "LifeMap.AI"
    API_VERSION: str = "0.2.0-phase2"
    API_TOKEN: str = os.getenv("API_TOKEN", "dev123")
    ENV: str = os.getenv("ENV", "dev")

    DB_HOST: str = os.getenv("DB_HOST", "db")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "lifemap")
    DB_USER: str = os.getenv("DB_USER", "lifemap")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "lifemap_pw")

settings = Settings()
