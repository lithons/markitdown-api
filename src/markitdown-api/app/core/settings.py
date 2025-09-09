from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "MarkItDown REST API"
    APP_DESC: str = "Convert documents to Markdown using Microsoft's MarkItDown library"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"  # development|staging|production

    # Server
    HOST: str = "0.0.0.0"     # good default for containers
    PORT: int = 8000

    # When running behind proxies / tunnels / gateways (Ocelot, Nginx, DevTunnels):
    PUBLIC_BASE_URL: Optional[AnyHttpUrl] = None  # e.g. https://api.example.com

    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = Field(default_factory=list)

    # Features
    ENABLE_SCALAR: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()