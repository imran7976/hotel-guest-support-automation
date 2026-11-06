from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # General
    PROJECT_NAME: str = "AI-Powered Hotel Guest Support Automation System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "change-this-ultra-secure-secret-key-in-production-hotel-guest-2025"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Server & CORS
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    # Database
    DATABASE_URL: str = "sqlite:///./hotel_support.db"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "hotel_guest_support"
    MYSQL_USER: str = "hotel_user"
    MYSQL_PASSWORD: str = "hotel_secure_pass_2025"

    # OpenAI & AI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    AI_CONFIDENCE_THRESHOLD: float = 0.75
    AI_TEMPERATURE: float = 0.2

    # n8n Automation
    N8N_WEBHOOK_URL_BASE: str = "http://localhost:5678/webhook"
    N8N_WEBHOOK_AUTH_TOKEN: str = "hotel_n8n_secure_token_xyz987"
    N8N_ENABLED: bool = True

    # Notifications & Hotel Details
    MOCK_DELIVERY: bool = True
    SUPPORT_TEAM_EMAIL: str = "support@grandhotelazure.demo"
    HOTEL_FRONTDESK_PHONE: str = "+1-555-0199"
    HOTEL_NAME: str = "Grand Azure Resort & Hotel"

    # Admin seed
    ADMIN_DEFAULT_EMAIL: str = "admin@grandhotelazure.demo"
    ADMIN_DEFAULT_PASSWORD: str = "AdminHotel2025!"
    ADMIN_DEFAULT_NAME: str = "Front Office Manager"


settings = Settings()

