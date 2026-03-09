"""
Text extraction service using EasyOCR
"""
import easyocr
import time
from typing import Tuple, Optional, Dict, Any, List
from PIL import Image
import io
import logging
import numpy as np

from app.core.exceptions import TextExtractionException

logger = logging.getLogger(__name__)


class TextExtractor:
    """Handles text extraction from images using EasyOCR"""
    
    def __init__(self):
        """Initialize EasyOCR reader"""
        try:
            logger.info("Initializing EasyOCR reader...")
            # Initialize with English language
            # gpu=False for CPU-only systems, set to True if GPU available
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            logger.info("EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {str(e)}")
            raise TextExtractionException(f"EasyOCR initialization failed: {str(e)}")
    
    def extract_text_with_confidence(self, image_bytes: bytes, 
                                   config: str = None) -> Tuple[str, float, Dict[str, Any]]:
        """
        Extract text from image with confidence scores
        
        Args:
            image_bytes: Image data as bytes
            config: Not used for EasyOCR (kept for compatibility)
            
        Returns:
            Tuple of (extracted_text, confidence_score, metadata)
        """
        start_time = time.time()
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert PIL Image to numpy array for EasyOCR
            image_np = np.array(image)
            
            # Extract text with EasyOCR
            # Returns list of (bbox, text, confidence)
            results = self.reader.readtext(image_np, detail=1)
            
            # Extract text and confidence
            extracted_lines = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if text.strip():
                    extracted_lines.append(text)
                    confidences.append(confidence)
            
            # Join all text with newlines
            extracted_text = "\n".join(extracted_lines)
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            processing_time = int((time.time() - start_time) * 1000)
            
            metadata = {
                'processing_time_ms': processing_time,
                'word_count': len(extracted_lines),
                'confidence_distribution': {
                    'high': len([c for c in confidences if c >= 0.8]),
                    'medium': len([c for c in confidences if 0.5 <= c < 0.8]),
                    'low': len([c for c in confidences if c < 0.5])
                },
                'ocr_engine': 'EasyOCR',
                'total_detections': len(results)
            }
            
            logger.info(f"Text extraction completed in {processing_time}ms with confidence {avg_confidence:.2f}")
            
            return extracted_text.strip(), avg_confidence, metadata
            
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise TextExtractionException(f"Text extraction failed: {str(e)}")
    
    def extract_text_simple(self, image_bytes: bytes, config: str = None) -> str:
        """
        Simple text extraction without confidence data
        
        Args:
            image_bytes: Image data as bytes
            config: Not used for EasyOCR (kept for compatibility)
            
        Returns:
            Extracted text string
        """
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            
            # Extract text (detail=0 returns only text, no bbox or confidence)
            results = self.reader.readtext(image_np, detail=0)
            
            # Join all text with newlines
            text = "\n".join(results)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Simple text extraction failed: {str(e)}")
            raise TextExtractionException(f"Text extraction failed: {str(e)}")
    
    def extract_with_language_hint(self, image_bytes: bytes, 
                                 language: str = 'en') -> Tuple[str, float]:
        """
        Extract text with specific language configuration
        
        Args:
            image_bytes: Image data as bytes
            language: Language code (e.g., 'en', 'fr', 'de')
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # For language-specific extraction, we'd need to reinitialize reader
            # For now, use default English reader
            text, confidence, _ = self.extract_text_with_confidence(image_bytes)
            return text, confidence
            
        except Exception as e:
            raise TextExtractionException(f"Language-specific extraction failed: {str(e)}")
    
    def get_available_languages(self) -> List[str]:
        """Get list of available EasyOCR languages"""
        try:
            # EasyOCR supports many languages
            # Return commonly used ones for code
            return ['en', 'ch_sim', 'ch_tra', 'ja', 'ko', 'fr', 'de', 'es', 'pt', 'ru']
        except Exception as e:
            logger.warning(f"Could not get available languages: {str(e)}")
            return ['en']  # Default fallback
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on EasyOCR service"""
        try:
            # Test with a simple image
            test_image = Image.new('RGB', (200, 100), color='white')
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(test_image)
            
            # Draw some test text
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            draw.text((10, 40), "Test OCR", fill='black', font=font)
            
            test_bytes = io.BytesIO()
            test_image.save(test_bytes, format='PNG')
            test_bytes = test_bytes.getvalue()
            
            # Try extraction
            start_time = time.time()
            text = self.extract_text_simple(test_bytes)
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                'status': 'healthy',
                'ocr_engine': 'EasyOCR',
                'available_languages': self.get_available_languages(),
                'response_time_ms': response_time,
                'test_extraction_successful': True,
                'test_result': text
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'ocr_engine': 'EasyOCR',
                'test_extraction_successful': False
            }