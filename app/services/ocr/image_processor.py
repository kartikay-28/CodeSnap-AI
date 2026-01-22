"""
Image preprocessing service for OCR optimization
"""
import logging
from typing import Tuple, Dict, Any, Optional
from PIL import Image
import io

from app.services.utils.image_utils import ImageUtils
from app.services.utils.file_validator import FileValidator
from app.schemas.ocr import ImageMetadata
from app.core.exceptions import ImageProcessingException

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles image preprocessing for optimal OCR results"""
    
    def __init__(self):
        self.image_utils = ImageUtils()
        self.file_validator = FileValidator()
    
    def process_uploaded_image(self, image_bytes: bytes, 
                             filename: str,
                             enhance_image: bool = True) -> Tuple[bytes, ImageMetadata, Dict[str, Any]]:
        """
        Process uploaded image for OCR
        
        Args:
            image_bytes: Raw image bytes
            filename: Original filename
            enhance_image: Whether to apply image enhancements
            
        Returns:
            Tuple of (processed_image_bytes, metadata, preprocessing_info)
        """
        try:
            # Validate image content and get dimensions
            original_dimensions = self.file_validator.validate_image_content(image_bytes)
            
            # Get image metadata
            with Image.open(io.BytesIO(image_bytes)) as img:
                metadata = ImageMetadata(
                    filename=filename,
                    size_bytes=len(image_bytes),
                    mime_type=f"image/{img.format.lower()}" if img.format else "image/unknown",
                    dimensions=original_dimensions,
                    dpi=img.info.get('dpi', (72, 72))[0] if img.info.get('dpi') else None
                )
            
            # Apply preprocessing
            if enhance_image:
                processed_bytes, preprocessing_info = self.image_utils.preprocess_for_ocr(
                    image_bytes, enhance_image=True
                )
                logger.info(f"Image preprocessing completed for {filename}")
            else:
                processed_bytes = image_bytes
                preprocessing_info = {'enhancement_skipped': True}
                logger.info(f"Image preprocessing skipped for {filename}")
            
            return processed_bytes, metadata, preprocessing_info
            
        except Exception as e:
            raise ImageProcessingException(f"Image processing failed for {filename}: {str(e)}")
    
    def create_ocr_optimized_image(self, image_bytes: bytes) -> bytes:
        """
        Create OCR-optimized version of image with aggressive preprocessing
        
        Args:
            image_bytes: Original image bytes
            
        Returns:
            Optimized image bytes
        """
        try:
            # Apply aggressive preprocessing for difficult images
            processed_bytes, _ = self.image_utils.preprocess_for_ocr(
                image_bytes, enhance_image=True
            )
            
            return processed_bytes
            
        except Exception as e:
            raise ImageProcessingException(f"OCR optimization failed: {str(e)}")
    
    def get_image_info(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Get detailed information about an image
        
        Args:
            image_bytes: Image data
            
        Returns:
            Dictionary with image information
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'dpi': img.info.get('dpi'),
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'color_count': len(img.getcolors(maxcolors=256)) if img.getcolors(maxcolors=256) else 'many',
                    'aspect_ratio': round(img.width / img.height, 2) if img.height > 0 else 0
                }
        except Exception as e:
            raise ImageProcessingException(f"Failed to get image info: {str(e)}")
    
    def validate_image_for_ocr(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Validate if image is suitable for OCR processing
        
        Args:
            image_bytes: Image data
            
        Returns:
            Validation results with recommendations
        """
        try:
            info = self.get_image_info(image_bytes)
            
            validation_result = {
                'is_suitable': True,
                'warnings': [],
                'recommendations': [],
                'score': 100  # Start with perfect score
            }
            
            # Check resolution
            width, height = info['size']
            total_pixels = width * height
            
            if total_pixels < 50000:  # Less than ~224x224
                validation_result['warnings'].append('Image resolution is quite low')
                validation_result['recommendations'].append('Consider using a higher resolution image')
                validation_result['score'] -= 20
            
            # Check aspect ratio
            if info['aspect_ratio'] > 5 or info['aspect_ratio'] < 0.2:
                validation_result['warnings'].append('Unusual aspect ratio detected')
                validation_result['recommendations'].append('Crop image to focus on text content')
                validation_result['score'] -= 10
            
            # Check if image is too small
            if width < 100 or height < 100:
                validation_result['warnings'].append('Image dimensions are very small')
                validation_result['recommendations'].append('Use image with minimum 300x300 pixels')
                validation_result['score'] -= 30
                validation_result['is_suitable'] = False
            
            # Check color mode
            if info['mode'] not in ['RGB', 'L', 'RGBA']:
                validation_result['warnings'].append(f"Unusual color mode: {info['mode']}")
                validation_result['recommendations'].append('Convert to RGB or grayscale')
                validation_result['score'] -= 15
            
            # DPI check
            if info['dpi'] and info['dpi'][0] < 150:
                validation_result['warnings'].append('Low DPI detected')
                validation_result['recommendations'].append('Use images with at least 300 DPI for better OCR')
                validation_result['score'] -= 10
            
            # Final suitability check
            if validation_result['score'] < 50:
                validation_result['is_suitable'] = False
            
            return validation_result
            
        except Exception as e:
            return {
                'is_suitable': False,
                'error': str(e),
                'warnings': ['Failed to validate image'],
                'recommendations': ['Check if image file is valid'],
                'score': 0
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on image processing capabilities"""
        try:
            # Test image processing with a simple test image
            test_image = Image.new('RGB', (200, 100), color='white')
            test_bytes = io.BytesIO()
            test_image.save(test_bytes, format='PNG')
            test_bytes = test_bytes.getvalue()
            
            # Test preprocessing
            processed_bytes, preprocessing_info = self.image_utils.preprocess_for_ocr(test_bytes)
            
            # Test validation
            validation_result = self.validate_image_for_ocr(test_bytes)
            
            return {
                'status': 'healthy',
                'opencv_available': True,
                'pillow_available': True,
                'preprocessing_functional': len(processed_bytes) > 0,
                'validation_functional': 'score' in validation_result,
                'test_processing_successful': True
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'test_processing_successful': False
            }