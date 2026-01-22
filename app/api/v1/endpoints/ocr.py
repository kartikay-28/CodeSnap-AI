"""
OCR API endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.schemas.ocr import OCRResponse, OCRResult, OCRHealthCheck
from app.services.ocr.ocr_service import OCRService
from app.core.exceptions import (
    OCRException, 
    FileValidationException,
    FileSizeException,
    FileTypeException
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get OCR service instance
def get_ocr_service() -> OCRService:
    return OCRService()


@router.post("/extract", response_model=OCRResponse, summary="Extract text from image")
async def extract_text_from_image(
    file: UploadFile = File(..., description="Image file to extract text from"),
    enhance_image: bool = Query(True, description="Apply image enhancement for better OCR"),
    extract_code_only: bool = Query(True, description="Focus on code extraction and cleaning"),
    language_hint: Optional[str] = Query(None, description="Programming language hint (python, javascript, etc.)"),
    ocr_service: OCRService = Depends(get_ocr_service)
):
    """
    Extract text from uploaded image using OCR.
    
    **Features:**
    - Validates file type and size
    - Preprocesses image for optimal OCR
    - Extracts text using Tesseract
    - Cleans and formats code text
    - Returns confidence scores and metadata
    
    **Supported formats:** PNG, JPG, JPEG, BMP, TIFF
    **Max file size:** 10MB
    """
    try:
        logger.info(f"OCR extraction request for file: {file.filename}")
        
        # Validate file is provided
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file provided"
            )
        
        # Process OCR
        result = await ocr_service.extract_text_from_upload(
            file=file,
            enhance_image=enhance_image,
            extract_code_only=extract_code_only,
            language_hint=language_hint
        )
        
        logger.info(f"OCR extraction successful for {file.filename}")
        
        return OCRResponse(
            success=True,
            result=result
        )
        
    except FileSizeException as e:
        logger.warning(f"File size validation failed: {str(e)}")
        raise HTTPException(status_code=413, detail=str(e))
        
    except FileTypeException as e:
        logger.warning(f"File type validation failed: {str(e)}")
        raise HTTPException(status_code=415, detail=str(e))
        
    except FileValidationException as e:
        logger.warning(f"File validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except OCRException as e:
        logger.error(f"OCR processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error during OCR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during OCR processing")


@router.post("/validate", summary="Validate image for OCR suitability")
async def validate_image_for_ocr(
    file: UploadFile = File(..., description="Image file to validate"),
    ocr_service: OCRService = Depends(get_ocr_service)
):
    """
    Validate if an uploaded image is suitable for OCR processing.
    
    **Returns:**
    - Suitability score (0-100)
    - Warnings about potential issues
    - Recommendations for improvement
    - Technical image information
    """
    try:
        logger.info(f"Image validation request for file: {file.filename}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        file_content = await file.read()
        
        # Validate image
        validation_result = ocr_service.validate_image_for_ocr(file_content)
        
        logger.info(f"Image validation completed for {file.filename}")
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "validation": validation_result
        })
        
    except FileValidationException as e:
        logger.warning(f"File validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Image validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Image validation failed")


@router.get("/health", response_model=OCRHealthCheck, summary="OCR service health check")
async def ocr_health_check(ocr_service: OCRService = Depends(get_ocr_service)):
    """
    Check the health status of OCR service components.
    
    **Checks:**
    - Tesseract installation and version
    - OpenCV availability
    - Pillow (PIL) availability
    - Basic functionality test
    """
    try:
        logger.info("OCR health check requested")
        
        health_status = ocr_service.health_check()
        
        # Map to response model
        response = OCRHealthCheck(
            tesseract_available=health_status.get('tesseract_available', False),
            tesseract_version=health_status.get('components', {}).get('text_extractor', {}).get('version'),
            opencv_available=health_status.get('opencv_available', False),
            pillow_available=health_status.get('pillow_available', False),
            status=health_status.get('status', 'unknown')
        )
        
        logger.info(f"OCR health check completed: {response.status}")
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return OCRHealthCheck(
            tesseract_available=False,
            opencv_available=False,
            pillow_available=False,
            status="unhealthy"
        )


@router.get("/info", summary="Get OCR service information")
async def get_ocr_info(ocr_service: OCRService = Depends(get_ocr_service)):
    """
    Get information about OCR service capabilities and configuration.
    """
    try:
        health_status = ocr_service.health_check()
        
        return JSONResponse(content={
            "service": "OCR Text Extraction",
            "version": "1.0.0",
            "capabilities": {
                "supported_formats": ["PNG", "JPG", "JPEG", "BMP", "TIFF"],
                "max_file_size_mb": 10,
                "image_preprocessing": True,
                "code_text_cleaning": True,
                "confidence_scoring": True,
                "language_detection": True
            },
            "components": {
                "tesseract": {
                    "available": health_status.get('tesseract_available', False),
                    "version": health_status.get('components', {}).get('text_extractor', {}).get('version')
                },
                "opencv": {
                    "available": health_status.get('opencv_available', False)
                },
                "pillow": {
                    "available": health_status.get('pillow_available', False)
                }
            },
            "status": health_status.get('status', 'unknown')
        })
        
    except Exception as e:
        logger.error(f"Failed to get OCR info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get service information")