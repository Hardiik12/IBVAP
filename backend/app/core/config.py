import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Backend Application Settings.
    Loads values from environment variables or .env file.
    """
    APP_NAME: str = "IBVAP Backend API"
    APP_ENV: str = Field(default="development", description="Options: development, staging, production")
    VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    EVIDENCE_ROOT: str = Field(default="data/evidence", description="Base directory for stored evidence snapshots")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://ibvap:ibvap@localhost:5432/ibvap",
        description="PostgreSQL Connection URL"
    )

    # JWT Security Settings
    JWT_SECRET_KEY: str = Field(
        default="replace-with-secure-random-secret-for-dev-only",
        description="Secret key for signing JWT access tokens"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")

    # CORS
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                import json
                try:
                    origins = json.loads(v)
                    return [str(i).strip() for i in origins if str(i).strip()]
                except Exception:
                    pass
            origins = [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            origins = [str(i).strip() for i in v if str(i).strip()]
        else:
            raise ValueError(v)

        if "*" in origins and len(origins) > 1:
            origins = [o for o in origins if o != "*"]
        return origins



    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
