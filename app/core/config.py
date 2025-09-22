from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Jagriti portal settings
    JAGRITI_BASE_URL: str = "https://e-jagriti.gov.in"
    JAGRITI_SEARCH_URL: str = "https://e-jagriti.gov.in/advance-case-search"
    
    # Request settings
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    DELAY_BETWEEN_REQUESTS: float = 1.0
    
    # User agent for requests
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()