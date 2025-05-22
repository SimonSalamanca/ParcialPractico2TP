# app/core/config.py
from pydantic import Field, AnyUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: AnyUrl = Field(..., env="MONGODB_URL")
    mongodb_db: str     = Field(..., env="MONGODB_DB")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
