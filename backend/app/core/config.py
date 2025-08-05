from pydantic_settings import BaseSettings
from typing import Optional, Union
import os
from dotenv import load_dotenv
from pydantic import field_validator

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Agentic Chat Assistant"
    VERSION: str = "1.0.0"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: Union[str, list[str]] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # AI Service Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    
    # Tool Configuration
    WEB_SEARCH_API_KEY: Optional[str] = None
    WEB_SEARCH_ENGINE_ID: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate required API keys
        if not self.OPENAI_API_KEY:
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            if not self.OPENAI_API_KEY:
                print("Warning: OPENAI_API_KEY not found in environment variables")

settings = Settings()
