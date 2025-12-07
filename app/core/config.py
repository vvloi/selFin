"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional
import os


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
    # You can set CORS_ORIGINS in the .env file as a comma-separated list,
    # or set it to '*' to allow all origins (useful for local development).
    cors_origins_env: Optional[str] = None

    # Default origins used when no env var provided
    _default_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def cors_origins(self) -> list[str]:
        """Return parsed CORS origins from env or defaults.

        - If `CORS_ORIGINS` is set to `*`, returns `['*']` to allow all origins.
        - If `CORS_ORIGINS` is a comma-separated list, splits and strips values.
        - Otherwise returns the default list.
        """
        # prefer explicit setting in pydantic (.env -> CORS_ORIGINS_ENV)
        val = None
        if self.cors_origins_env:
            val = self.cors_origins_env.strip()
        # fallback to environment variable name CORS_ORIGINS (common pattern)
        if not val:
            env_val = os.getenv("CORS_ORIGINS")
            if env_val:
                val = env_val.strip()
        if val:
            if val == "*":
                return ["*"]
            # split by comma and strip whitespace, ignore empty entries
            parts = [p.strip() for p in val.split(",") if p.strip()]
            if parts:
                return parts
        return list(self._default_cors_origins)
    
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
