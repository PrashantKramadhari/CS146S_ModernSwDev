"""Application configuration management."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Try Pydantic v1 fallback, but handle Pydantic v2 case
    try:
        from pydantic import BaseSettings
    except Exception as e:
        # In Pydantic v2, accessing BaseSettings raises PydanticImportError
        # Check error message to provide helpful guidance
        error_str = str(e).lower()
        if "basesettings" in error_str or "pydantic-settings" in error_str:
            raise ImportError(
                "pydantic-settings is required for Pydantic v2. "
                "Install it with: pip install pydantic-settings"
            ) from e
        # Re-raise if it's a different error
        raise


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database settings
    database_path: Path = Path(__file__).resolve().parents[1] / "data" / "app.db"
    data_dir: Path = Path(__file__).resolve().parents[1] / "data"
    
    # Ollama settings
    # Note: Ensure the model is installed with: ollama pull llama3.1
    # You can also use tags like "llama3.1:latest" or "llama3.1:8b"
    ollama_model: str = "llama3.1:8b"
    ollama_base_url: Optional[str] = None
    
    # Application settings
    app_title: str = "Action Item Extractor"
    app_debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings

