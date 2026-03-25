"""
Kimi CLI Backend Configuration
"""

import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Uygulama ayarları"""

    # API
    moonshot_api_key: str = Field(default="", env="MOONSHOT_API_KEY")
    moonshot_base_url: str = "https://api.moonshot.ai/v1"

    # Model - moonshot-v1-128k daha stabil tool calling için
    default_model: str = "moonshot-v1-128k"
    max_tokens: int = 8192
    temperature: float = 0.7

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Workspace
    workspace_dir: str = "./workspace"
    sessions_dir: str = "./sessions"

    # Security
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".py", ".js", ".ts", ".json", ".yaml", ".yml", ".md", ".txt", ".html", ".css"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
