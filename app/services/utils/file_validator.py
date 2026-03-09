"""
File validation utilities for image uploads
"""
from fastapi import UploadFile
from typing import Tuple
from PIL import Image
import io
import imghdr

from app.core.config import settings
from app.core.exceptions import (
    FileValidationException,
    FileSizeException,
    FileTypeException
)


class FileValidator:
    """Validates uploaded image files"""
    
    @staticmethod
    def validate_file_size(file: UploadFile) -> None:
        """Validate file size doesn't exceed limit"""
        if hasattr(file.file, 'seek') and hasattr(file.file, 'tell'):
            # Get current position
            current_pos = file.file.tell()
            # Seek to end to get size
            file.file.seek(0, 2)
            size = file.file.tell()
            # Reset to original position
            file.file.seek(current_pos)
            
            if size > settings.MAX_FILE_SIZE_BYTES:
                raise FileSizeException(
                    f"File size {size} bytes exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES} bytes"
                )
    
    @staticmethod
    def validate_file_type(file: UploadFile) -> str:
        """Validate file type and return MIME type"""
        # Check file extension
        if file.filename:
            extension = file.filename.lower().split('.')[-1]
            allowed_exts = settings.allowed_extensions_list
            if extension not in allowed_exts:
                raise FileTypeException(
                    f"File extension '{extension}' not allowed. Allowed: {', '.join(allowed_exts)}"
                )
        
        # Read file content for type detection
        file_content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        # Detect image type using imghdr
        try:
            image_type = imghdr.what(None, h=file_content)
            if image_type:
                mime_type = f"image/{image_type}"
            else:
                # Fallback to content type from upload
                mime_type = file.content_type or "application/octet-stream"
        except Exception:
            mime_type = file.content_type or "application/octet-stream"
        
        # Validate MIME type
        allowed_mimes = settings.allowed_mime_types_list
        if not any(mime_type.startswith(allowed.split('/')[0]) for allowed in allowed_mimes):
            raise FileTypeException(
                f"MIME type '{mime_type}' not allowed. Must be an image file."
            )
        
        return mime_type
    
    @staticmethod
    def validate_image_content(file_content: bytes) -> Tuple[int, int]:
        """Validate image can be opened and return dimensions"""
        try:
            with Image.open(io.BytesIO(file_content)) as img:
                return img.size
        except Exception as e:
            raise FileValidationException(f"Invalid image content: {str(e)}")
    
    @classmethod
    def validate_upload(cls, file: UploadFile) -> Tuple[str, Tuple[int, int], bytes]:
        """
        Complete file validation pipeline
        
        Returns:
            Tuple of (mime_type, dimensions, file_content)
        """
        # Validate file size
        cls.validate_file_size(file)
        
        # Validate file type
        mime_type = cls.validate_file_type(file)
        
        # Read file content
        file_content = file.file.read()
        file.file.seek(0)  # Reset for potential reuse
        
        # Validate image content and get dimensions
        dimensions = cls.validate_image_content(file_content)
        
        return mime_type, dimensions, file_content