"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # LLM Configuration
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    
    # OCR Configuration
    TESSERACT_PATH: str = "/usr/bin/tesseract"
    TESSERACT_CONFIG: str = "--oem 3 --psm 6"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["png", "jpg", "jpeg", "bmp", "tiff"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()