"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Personal Finance API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    # Must be set via DATABASE_URL environment variable in .env file
    database_url: str
    
    # Example for local SQLite (development only, not recommended for production)
    # database_url: str = "sqlite:///./finance.db"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # Password hashing
    bcrypt_rounds: int = 12
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 100
    
    # Budget thresholds
    budget_near_limit_threshold: float = 0.8  # 80%
    budget_exceeded_threshold: float = 1.0  # 100%
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
