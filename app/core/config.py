"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # LLM Configuration
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    DEFAULT_LLM_PROVIDER: str = "gemini"
    DEFAULT_MODEL: str = "gemini-2.0-flash-exp"
    
    # OCR Configuration (EasyOCR)
    OCR_LANGUAGES: str = "en"  # Comma-separated list
    OCR_GPU: bool = False  # Set to True if GPU available
    
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
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: str = "png,jpg,jpeg,bmp,tiff"  # Comma-separated
    ALLOWED_MIME_TYPES: str = "image/png,image/jpeg,image/jpg,image/bmp,image/tiff"  # Comma-separated
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as a list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def allowed_mime_types_list(self) -> List[str]:
        """Get allowed MIME types as a list"""
        return [mime.strip() for mime in self.ALLOWED_MIME_TYPES.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()