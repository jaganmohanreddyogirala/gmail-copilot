import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # API Security & Authentication
    API_SECRET_KEY: str = "copilot-prod-secret-key-2026"
    ENABLE_AUTH: bool = False
    RATE_LIMIT_ENABLED: bool = True
    AUTO_SEND_LOW_RISK_REPLIES: bool = False



    # Google OAuth 2.0 Credentials
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    # Gmail File Paths
    GMAIL_TOKEN_PATH: str = "token.json"
    GMAIL_CREDENTIALS_PATH: str = "credentials.json"

    # Gmail Scopes required for reading emails and creating drafts (No auto-sending)
    GMAIL_SCOPES: List[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    # Database URL (Defaults to PostgreSQL, fallbacks handled gracefully)
    DATABASE_URL: str = "sqlite+aiosqlite:///./gmail_copilot.db"

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"

    # MCP Integration Settings
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_REPO: Optional[str] = None

    # Evaluation Config
    EVAL_DATASET_PATH: str = "app/eval/dataset.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

