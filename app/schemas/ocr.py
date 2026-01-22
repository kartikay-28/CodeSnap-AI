"""
OCR-related Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class OCRRequest(BaseModel):
    """Request model for OCR processing"""
    enhance_image: bool = Field(default=True, description="Apply image enhancement for better OCR")
    extract_code_only: bool = Field(default=True, description="Focus on code extraction")
    language_hint: Optional[str] = Field(default=None, description="Programming language hint")


class ImageMetadata(BaseModel):
    """Image metadata information"""
    filename: str
    size_bytes: int
    mime_type: str
    dimensions: tuple[int, int]
    dpi: Optional[int] = None


class OCRResult(BaseModel):
    """OCR extraction result"""
    extracted_text: str = Field(description="Raw extracted text from image")
    confidence_score: float = Field(ge=0.0, le=1.0, description="OCR confidence score")
    processing_time_ms: int = Field(description="Processing time in milliseconds")
    image_metadata: ImageMetadata
    preprocessing_applied: Dict[str, Any] = Field(description="Applied preprocessing steps")


class OCRResponse(BaseModel):
    """Complete OCR API response"""
    success: bool
    result: Optional[OCRResult] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OCRHealthCheck(BaseModel):
    """OCR service health check response"""
    tesseract_available: bool
    tesseract_version: Optional[str] = None
    opencv_available: bool
    pillow_available: bool
    status: str  # "healthy", "degraded", "unhealthy"