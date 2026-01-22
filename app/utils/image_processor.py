"""
Image processing utilities for OCR enhancement
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io
from typing import Tuple, Dict, Any

from app.core.config import settings
from app.core.exceptions import ImageProcessingException


class ImageProcessor:
    """Image preprocessing utilities for better OCR accuracy"""
    
    @staticmethod
    def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format"""
        try:
            # Convert PIL to RGB if not already
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array and change color order (RGB -> BGR)
            cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return cv2_image
        except Exception as e:
            raise ImageProcessingException(f"Failed to convert PIL to CV2: {str(e)}")
    
    @staticmethod
    def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
        """Convert OpenCV image to PIL format"""
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb_image)
        except Exception as e:
            raise ImageProcessingException(f"Failed to convert CV2 to PIL: {str(e)}")
    
    @staticmethod
    def enhance_contrast_brightness(image: Image.Image, 
                                  contrast_factor: float = None,
                                  brightness_factor: float = None) -> Image.Image:
        """Enhance image contrast and brightness"""
        try:
            contrast_factor = contrast_factor or settings.CONTRAST_FACTOR
            brightness_factor = brightness_factor or settings.BRIGHTNESS_FACTOR
            
            # Enhance contrast
            contrast_enhancer = ImageEnhance.Contrast(image)
            image = contrast_enhancer.enhance(contrast_factor)
            
            # Enhance brightness
            brightness_enhancer = ImageEnhance.Brightness(image)
            image = brightness_enhancer.enhance(brightness_factor)
            
            return image
        except Exception as e:
            raise ImageProcessingException(f"Failed to enhance contrast/brightness: {str(e)}")
    
    @staticmethod
    def apply_gaussian_blur(cv2_image: np.ndarray, kernel_size: int = None) -> np.ndarray:
        """Apply Gaussian blur to reduce noise"""
        try:
            kernel_size = kernel_size or settings.GAUSSIAN_BLUR_KERNEL
            if kernel_size > 0:
                # Ensure kernel size is odd
                if kernel_size % 2 == 0:
                    kernel_size += 1
                return cv2.GaussianBlur(cv2_image, (kernel_size, kernel_size), 0)
            return cv2_image
        except Exception as e:
            raise ImageProcessingException(f"Failed to apply Gaussian blur: {str(e)}")
    
    @staticmethod
    def convert_to_grayscale(cv2_image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        try:
            if len(cv2_image.shape) == 3:
                return cv2.cvtColor(cv2_image, cv2.COLOR_BGR2GRAY)
            return cv2_image
        except Exception as e:
            raise ImageProcessingException(f"Failed to convert to grayscale: {str(e)}")
    
    @staticmethod
    def apply_threshold(gray_image: np.ndarray, threshold_type: str = "adaptive") -> np.ndarray:
        """Apply thresholding for better text extraction"""
        try:
            if threshold_type == "adaptive":
                return cv2.adaptiveThreshold(
                    gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
            elif threshold_type == "otsu":
                _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                return thresh
            else:
                _, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
                return thresh
        except Exception as e:
            raise ImageProcessingException(f"Failed to apply threshold: {str(e)}")
    
    @staticmethod
    def remove_noise(cv2_image: np.ndarray) -> np.ndarray:
        """Remove noise using morphological operations"""
        try:
            # Create kernel for morphological operations
            kernel = np.ones((1, 1), np.uint8)
            
            # Apply opening (erosion followed by dilation)
            opening = cv2.morphologyEx(cv2_image, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Apply closing (dilation followed by erosion)
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            return closing
        except Exception as e:
            raise ImageProcessingException(f"Failed to remove noise: {str(e)}")
    
    @staticmethod
    def resize_for_ocr(image: Image.Image, target_dpi: int = None) -> Image.Image:
        """Resize image to optimal DPI for OCR"""
        try:
            target_dpi = target_dpi or settings.IMAGE_DPI
            
            # Get current DPI
            current_dpi = image.info.get('dpi', (72, 72))
            if isinstance(current_dpi, tuple):
                current_dpi = current_dpi[0]
            
            # Calculate scale factor
            scale_factor = target_dpi / current_dpi
            
            # Only resize if significant difference
            if abs(scale_factor - 1.0) > 0.1:
                new_size = (
                    int(image.width * scale_factor),
                    int(image.height * scale_factor)
                )
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            return image
        except Exception as e:
            raise ImageProcessingException(f"Failed to resize image: {str(e)}")
    
    @classmethod
    def preprocess_for_ocr(cls, image_bytes: bytes, 
                          enhance_image: bool = True) -> Tuple[bytes, Dict[str, Any]]:
        """
        Complete image preprocessing pipeline for OCR
        
        Args:
            image_bytes: Raw image bytes
            enhance_image: Whether to apply enhancements
            
        Returns:
            Tuple of (processed_image_bytes, preprocessing_metadata)
        """
        preprocessing_steps = {}
        
        try:
            # Load image
            pil_image = Image.open(io.BytesIO(image_bytes))
            preprocessing_steps['original_size'] = pil_image.size
            preprocessing_steps['original_mode'] = pil_image.mode
            
            if enhance_image:
                # Resize for optimal OCR
                pil_image = cls.resize_for_ocr(pil_image)
                preprocessing_steps['resized'] = True
                preprocessing_steps['final_size'] = pil_image.size
                
                # Enhance contrast and brightness
                pil_image = cls.enhance_contrast_brightness(pil_image)
                preprocessing_steps['contrast_enhanced'] = True
                preprocessing_steps['brightness_enhanced'] = True
                
                # Convert to OpenCV format for advanced processing
                cv2_image = cls.pil_to_cv2(pil_image)
                
                # Apply Gaussian blur to reduce noise
                cv2_image = cls.apply_gaussian_blur(cv2_image)
                preprocessing_steps['gaussian_blur_applied'] = True
                
                # Convert to grayscale
                gray_image = cls.convert_to_grayscale(cv2_image)
                preprocessing_steps['converted_to_grayscale'] = True
                
                # Apply adaptive thresholding
                thresh_image = cls.apply_threshold(gray_image, "adaptive")
                preprocessing_steps['adaptive_threshold_applied'] = True
                
                # Remove noise
                clean_image = cls.remove_noise(thresh_image)
                preprocessing_steps['noise_removed'] = True
                
                # Convert back to PIL
                pil_image = Image.fromarray(clean_image)
            
            # Convert to bytes
            output_buffer = io.BytesIO()
            pil_image.save(output_buffer, format='PNG')
            processed_bytes = output_buffer.getvalue()
            
            return processed_bytes, preprocessing_steps
            
        except Exception as e:
            raise ImageProcessingException(f"Image preprocessing failed: {str(e)}")
    
    @classmethod
    def validate_image_for_ocr(cls, image_bytes: bytes) -> Dict[str, Any]:
        """
        Validate if image is suitable for OCR processing
        
        Args:
            image_bytes: Image data to validate
            
        Returns:
            Validation results with recommendations
        """
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                validation_result = {
                    'is_suitable': True,
                    'warnings': [],
                    'recommendations': [],
                    'score': 100  # Start with perfect score
                }
                
                # Check resolution
                width, height = img.size
                total_pixels = width * height
                
                if total_pixels < 50000:  # Less than ~224x224
                    validation_result['warnings'].append('Image resolution is quite low')
                    validation_result['recommendations'].append('Consider using a higher resolution image')
                    validation_result['score'] -= 20
                
                # Check aspect ratio
                aspect_ratio = width / height if height > 0 else 0
                if aspect_ratio > 5 or aspect_ratio < 0.2:
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
                if img.mode not in ['RGB', 'L', 'RGBA']:
                    validation_result['warnings'].append(f"Unusual color mode: {img.mode}")
                    validation_result['recommendations'].append('Convert to RGB or grayscale')
                    validation_result['score'] -= 15
                
                # DPI check
                dpi = img.info.get('dpi')
                if dpi and dpi[0] < 150:
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