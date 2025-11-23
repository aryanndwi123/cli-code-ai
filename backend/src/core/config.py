import os
import secrets
from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./klix_code.db")

    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT tokens. Should be set via environment variable in production."
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v):
        """Validate SECRET_KEY from environment or generate secure default"""
        if not v or v == "your-secret-key-change-in-production":
            return secrets.token_urlsafe(32)
        return v

    # API
    API_HOST: str = os.getenv("API_HOST", "localhost")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # LLM Integration
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # File paths
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "./uploads")
    TEMP_DIRECTORY: str = os.getenv("TEMP_DIRECTORY", "./temp")

    # Redis (for caching and session management)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    class Config:
        env_file = "../.env"
        extra = "ignore"


# Global settings instance
settings = Settings()