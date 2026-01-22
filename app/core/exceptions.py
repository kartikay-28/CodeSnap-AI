"""
Custom exceptions for CodeSnap AI
"""

class CodeSnapException(Exception):
    """Base exception for CodeSnap AI"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class OCRException(CodeSnapException):
    """OCR processing failed"""
    pass

class ImageProcessingException(CodeSnapException):
    """Image preprocessing failed"""
    pass

class TextExtractionException(CodeSnapException):
    """Text extraction from image failed"""
    pass

class FileValidationException(CodeSnapException):
    """File validation failed"""
    pass

class FileSizeException(FileValidationException):
    """File size exceeds limit"""
    pass

class FileTypeException(FileValidationException):
    """Invalid file type"""
    pass

class LLMException(CodeSnapException):
    """LLM service error"""
    pass

class CodeCleaningException(CodeSnapException):
    """Code cleaning failed"""
    pass

class InvalidImageException(CodeSnapException):
    """Invalid image format or content"""
    pass

class ConfigurationException(CodeSnapException):
    """Configuration error"""
    pass