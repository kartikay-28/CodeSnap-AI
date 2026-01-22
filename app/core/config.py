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
    TESSERACT_TIMEOUT: int = 30
    
    # Image Processing Settings
    IMAGE_DPI: int = 300
    CONTRAST_FACTOR: float = 1.5
    BRIGHTNESS_FACTOR: float = 1.2
    GAUSSIAN_BLUR_KERNEL: int = 1
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = 10
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = ["png", "jpg", "jpeg", "bmp", "tiff"]
    ALLOWED_MIME_TYPES: List[str] = ["image/png", "image/jpeg", "image/jpg", "image/bmp", "image/tiff"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()