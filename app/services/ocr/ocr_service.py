"""
Main OCR service orchestrating the complete OCR pipeline
"""
import time
import logging
from typing import Optional, Dict, Any
from fastapi import UploadFile

from app.schemas.ocr import OCRResult, ImageMetadata
from app.services.ocr.text_extractor import TextExtractor
from app.services.ocr.image_processor import ImageProcessor
from app.services.utils.file_validator import FileValidator
from app.services.utils.text_cleaner import TextCleaner
from app.core.exceptions import OCRException, FileValidationException

logger = logging.getLogger(__name__)


class OCRService:
    """
    Main OCR service that orchestrates the complete pipeline:
    File Validation -> Image Processing -> Text Extraction -> Text Cleaning
    """
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.image_processor = ImageProcessor()
        self.file_validator = FileValidator()
        self.text_cleaner = TextCleaner()
    
    async def extract_text_from_upload(self, 
                                     file: UploadFile,
                                     enhance_image: bool = True,
                                     extract_code_only: bool = True,
                                     language_hint: Optional[str] = None) -> OCRResult:
        """
        Complete OCR pipeline for uploaded files
        
        Args:
            file: Uploaded file
            enhance_image: Apply image preprocessing
            extract_code_only: Focus on code extraction and cleaning
            language_hint: Programming language hint for better cleaning
            
        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting OCR processing for file: {file.filename}")
            
            # Step 1: Validate uploaded file
            mime_type, dimensions, file_content = self.file_validator.validate_upload(file)
            logger.info(f"File validation completed: {mime_type}, {dimensions}")
            
            # Step 2: Process image for OCR
            processed_image_bytes, image_metadata, preprocessing_info = (
                self.image_processor.process_uploaded_image(
                    file_content, file.filename or "unknown", enhance_image
                )
            )
            logger.info("Image preprocessing completed")
            
            # Step 3: Extract text using OCR
            raw_text, ocr_confidence, extraction_metadata = (
                self.text_extractor.extract_text_with_confidence(processed_image_bytes)
            )
            logger.info(f"Text extraction completed with confidence: {ocr_confidence:.2f}")
            
            # Step 4: Clean and enhance extracted text (if code extraction requested)
            if extract_code_only and raw_text.strip():
                cleaning_result = self.text_cleaner.clean_extracted_text(
                    raw_text, language_hint
                )
                final_text = cleaning_result['cleaned_text']
                
                # Add cleaning metadata to preprocessing info
                preprocessing_info.update({
                    'text_cleaning_applied': True,
                    'detected_language': cleaning_result['detected_language'],
                    'language_confidence': cleaning_result['language_confidence'],
                    'text_reduction_ratio': cleaning_result['reduction_ratio']
                })
                
                logger.info(f"Text cleaning completed. Detected language: {cleaning_result['detected_language']}")
            else:
                final_text = raw_text
                preprocessing_info['text_cleaning_applied'] = False
            
            # Calculate total processing time
            total_processing_time = int((time.time() - start_time) * 1000)
            
            # Create result
            result = OCRResult(
                extracted_text=final_text,
                confidence_score=ocr_confidence,
                processing_time_ms=total_processing_time,
                image_metadata=image_metadata,
                preprocessing_applied=preprocessing_info
            )
            
            logger.info(f"OCR processing completed in {total_processing_time}ms")
            return result
            
        except FileValidationException:
            # Re-raise file validation errors as-is
            raise
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            raise OCRException(f"OCR processing failed: {str(e)}")
    
    def extract_text_from_bytes(self, 
                              image_bytes: bytes,
                              filename: str = "image",
                              enhance_image: bool = True,
                              extract_code_only: bool = True,
                              language_hint: Optional[str] = None) -> OCRResult:
        """
        OCR pipeline for raw image bytes
        
        Args:
            image_bytes: Raw image data
            filename: Filename for metadata
            enhance_image: Apply image preprocessing
            extract_code_only: Focus on code extraction and cleaning
            language_hint: Programming language hint
            
        Returns:
            OCRResult with extracted text and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting OCR processing for bytes: {filename}")
            
            # Step 1: Validate image content
            dimensions = self.file_validator.validate_image_content(image_bytes)
            
            # Create basic metadata
            image_metadata = ImageMetadata(
                filename=filename,
                size_bytes=len(image_bytes),
                mime_type="image/unknown",
                dimensions=dimensions
            )
            
            # Step 2: Process image
            processed_image_bytes, _, preprocessing_info = (
                self.image_processor.process_uploaded_image(
                    image_bytes, filename, enhance_image
                )
            )
            
            # Step 3: Extract text
            raw_text, ocr_confidence, _ = (
                self.text_extractor.extract_text_with_confidence(processed_image_bytes)
            )
            
            # Step 4: Clean text if requested
            if extract_code_only and raw_text.strip():
                cleaning_result = self.text_cleaner.clean_extracted_text(
                    raw_text, language_hint
                )
                final_text = cleaning_result['cleaned_text']
                preprocessing_info.update({
                    'text_cleaning_applied': True,
                    'detected_language': cleaning_result['detected_language'],
                    'language_confidence': cleaning_result['language_confidence']
                })
            else:
                final_text = raw_text
                preprocessing_info['text_cleaning_applied'] = False
            
            total_processing_time = int((time.time() - start_time) * 1000)
            
            return OCRResult(
                extracted_text=final_text,
                confidence_score=ocr_confidence,
                processing_time_ms=total_processing_time,
                image_metadata=image_metadata,
                preprocessing_applied=preprocessing_info
            )
            
        except Exception as e:
            logger.error(f"OCR processing failed for bytes: {str(e)}")
            raise OCRException(f"OCR processing failed: {str(e)}")
    
    def validate_image_for_ocr(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Validate if an image is suitable for OCR processing
        
        Args:
            image_bytes: Image data to validate
            
        Returns:
            Validation results with recommendations
        """
        try:
            return self.image_processor.validate_image_for_ocr(image_bytes)
        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            return {
                'is_suitable': False,
                'error': str(e),
                'warnings': ['Validation failed'],
                'recommendations': ['Check if image is valid'],
                'score': 0
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check for the OCR service
        
        Returns:
            Health status of all OCR components
        """
        try:
            # Check individual components
            text_extractor_health = self.text_extractor.health_check()
            image_processor_health = self.image_processor.health_check()
            
            # Overall status
            overall_healthy = (
                text_extractor_health.get('status') == 'healthy' and
                image_processor_health.get('status') == 'healthy'
            )
            
            return {
                'status': 'healthy' if overall_healthy else 'unhealthy',
                'components': {
                    'text_extractor': text_extractor_health,
                    'image_processor': image_processor_health
                },
                'tesseract_available': text_extractor_health.get('test_extraction_successful', False),
                'opencv_available': image_processor_health.get('opencv_available', False),
                'pillow_available': image_processor_health.get('pillow_available', False)
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'components': {},
                'tesseract_available': False,
                'opencv_available': False,
                'pillow_available': False
            }