"""
Service interfaces - Clean architecture with dependency inversion
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from fastapi import UploadFile

class LLMServiceInterface(ABC):
    """Abstract interface for LLM providers"""
    
    @abstractmethod
    async def generate_completion(
        self, 
        prompt: str, 
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate text completion from prompt"""
        pass
    
    @abstractmethod
    async def generate_structured_response(
        self, 
        prompt: str, 
        schema: Dict[str, Any],
        model: str = None
    ) -> Dict[str, Any]:
        """Generate structured JSON response"""
        pass

class OCRServiceInterface(ABC):
    """Abstract interface for OCR processing"""
    
    @abstractmethod
    async def extract_text_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract text from image
        Returns: {
            'text': str,
            'confidence': float,
            'bounding_boxes': List[Dict],
            'preprocessing_applied': List[str]
        }
        """
        pass

class CodeCleanerServiceInterface(ABC):
    """Abstract interface for code cleaning"""
    
    @abstractmethod
    async def clean_ocr_text(self, raw_text: str, language_hint: str = None) -> Dict[str, Any]:
        """
        Clean OCR text and fix common errors
        Returns: {
            'cleaned_code': str,
            'detected_language': str,
            'confidence': float,
            'corrections_applied': List[str]
        }
        """
        pass