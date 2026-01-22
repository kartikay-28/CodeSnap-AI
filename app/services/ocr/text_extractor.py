"""
Text extraction service using Tesseract OCR
"""
import pytesseract
import subprocess
import time
from typing import Tuple, Optional, Dict, Any
from PIL import Image
import io
import logging

from app.core.config import settings
from app.core.exceptions import TextExtractionException, ConfigurationException

logger = logging.getLogger(__name__)


class TextExtractor:
    """Handles text extraction from images using Tesseract OCR"""
    
    def __init__(self):
        self._validate_tesseract_installation()
    
    def _validate_tesseract_installation(self) -> None:
        """Validate Tesseract is properly installed and accessible"""
        try:
            # Try to get Tesseract version
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
        except Exception as e:
            raise ConfigurationException(
                f"Tesseract OCR not found or not properly installed: {str(e)}"
            )
    
    def get_tesseract_version(self) -> Optional[str]:
        """Get Tesseract version string"""
        try:
            version = pytesseract.get_tesseract_version()
            return str(version)
        except Exception:
            return None
    
    def extract_text_with_confidence(self, image_bytes: bytes, 
                                   config: str = None) -> Tuple[str, float, Dict[str, Any]]:
        """
        Extract text from image with confidence scores
        
        Args:
            image_bytes: Image data as bytes
            config: Custom Tesseract configuration
            
        Returns:
            Tuple of (extracted_text, confidence_score, metadata)
        """
        start_time = time.time()
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Use provided config or default
            tesseract_config = config or settings.TESSERACT_CONFIG
            
            # Extract text with confidence data
            data = pytesseract.image_to_data(
                image, 
                config=tesseract_config,
                output_type=pytesseract.Output.DICT,
                timeout=settings.TESSERACT_TIMEOUT
            )
            
            # Extract text
            extracted_text = pytesseract.image_to_string(
                image,
                config=tesseract_config,
                timeout=settings.TESSERACT_TIMEOUT
            )
            
            # Calculate confidence score
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            confidence_score = avg_confidence / 100.0  # Convert to 0-1 range
            
            processing_time = int((time.time() - start_time) * 1000)
            
            metadata = {
                'processing_time_ms': processing_time,
                'word_count': len([word for word in data['text'] if word.strip()]),
                'confidence_distribution': {
                    'high': len([c for c in confidences if c >= 80]),
                    'medium': len([c for c in confidences if 50 <= c < 80]),
                    'low': len([c for c in confidences if c < 50])
                },
                'tesseract_config': tesseract_config
            }
            
            return extracted_text.strip(), confidence_score, metadata
            
        except subprocess.TimeoutExpired:
            raise TextExtractionException(
                f"OCR processing timed out after {settings.TESSERACT_TIMEOUT} seconds"
            )
        except Exception as e:
            raise TextExtractionException(f"Text extraction failed: {str(e)}")
    
    def extract_text_simple(self, image_bytes: bytes, config: str = None) -> str:
        """
        Simple text extraction without confidence data
        
        Args:
            image_bytes: Image data as bytes
            config: Custom Tesseract configuration
            
        Returns:
            Extracted text string
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            tesseract_config = config or settings.TESSERACT_CONFIG
            
            text = pytesseract.image_to_string(
                image,
                config=tesseract_config,
                timeout=settings.TESSERACT_TIMEOUT
            )
            
            return text.strip()
            
        except subprocess.TimeoutExpired:
            raise TextExtractionException(
                f"OCR processing timed out after {settings.TESSERACT_TIMEOUT} seconds"
            )
        except Exception as e:
            raise TextExtractionException(f"Text extraction failed: {str(e)}")
    
    def extract_with_language_hint(self, image_bytes: bytes, 
                                 language: str = 'eng') -> Tuple[str, float]:
        """
        Extract text with specific language configuration
        
        Args:
            image_bytes: Image data as bytes
            language: Tesseract language code (e.g., 'eng', 'fra', 'deu')
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # Create language-specific config
            config = f"{settings.TESSERACT_CONFIG} -l {language}"
            
            text, confidence, _ = self.extract_text_with_confidence(image_bytes, config)
            return text, confidence
            
        except Exception as e:
            raise TextExtractionException(f"Language-specific extraction failed: {str(e)}")
    
    def get_available_languages(self) -> list:
        """Get list of available Tesseract languages"""
        try:
            languages = pytesseract.get_languages()
            return languages
        except Exception as e:
            logger.warning(f"Could not get available languages: {str(e)}")
            return ['eng']  # Default fallback
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Tesseract service"""
        try:
            # Test with a simple image
            test_image = Image.new('RGB', (100, 50), color='white')
            test_bytes = io.BytesIO()
            test_image.save(test_bytes, format='PNG')
            test_bytes = test_bytes.getvalue()
            
            # Try extraction
            start_time = time.time()
            text = self.extract_text_simple(test_bytes)
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                'status': 'healthy',
                'version': self.get_tesseract_version(),
                'available_languages': self.get_available_languages(),
                'response_time_ms': response_time,
                'test_extraction_successful': True
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'version': self.get_tesseract_version(),
                'test_extraction_successful': False
            }