"""
Configuration settings for the IT Support Systems backend.
Environment variables and application settings.
"""
from typing import List, Literal
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API Configuration
    app_name: str = "IT Support Systems"
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    # LLM Provider Configuration
    llm_provider: Literal["openai", "gemini"] = "gemini"  # Default to Gemini
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    
    # Google Gemini Configuration
    google_api_key: str = ""
    gemini_model: str = "models/gemini-3.1-flash-lite"
    gemini_temperature: float = 0.7
    
    # Embedding Configuration
    embedding_provider: Literal["openai", "gemini"] = "gemini"
    embedding_model: str = "models/gemini-embedding-001"  # Gemini embedding
    
    # Database Configuration
    database_url: str = "sqlite:///./data/processed/it_support_systems.db"
    
    # Vector Database Configuration
    chroma_persist_directory: str = "./data/processed/chroma_db"
    
    # Remediation execution driver: "simulated", "powershell" or "auto".
    # "auto" uses powershell on Windows and the simulated driver elsewhere.
    execution_driver: str = "auto"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:8000,http://localhost:5173,http://138.68.228.105:3000,http://138.68.228.105:8000,http://138.68.228.105,http://www.prompto.gimhana.live,http://prompto.gimhana.live"
    
    # Logging
    log_level: str = "INFO"

    # Conversation behavior
    conversation_llm_first: bool = True
    
    #: Origins on the local network, allowed by pattern rather than by listing
    #: each one. The test machine reaches this backend by the host's LAN
    #: address, and that address changes whenever DHCP hands out a new one -
    #: so pinning it in a list means the app breaks on the next reconnect.
    #:
    #: Only private ranges match (192.168.x, 10.x, 172.16-31.x, loopback), so
    #: this opens nothing to the internet. Set it to "" to disable.
    allowed_origin_regex: str = (
        r"http://(localhost|127\.0\.0\.1|\[::1\]"
        r"|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        r"|192\.168\.\d{1,3}\.\d{1,3}"
        r"|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(:\d+)?"
    )

    def get_allowed_origins_list(self) -> List[str]:
        """Convert the comma-separated string to a list."""
        if isinstance(self.allowed_origins, list):
            return self.allowed_origins
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
