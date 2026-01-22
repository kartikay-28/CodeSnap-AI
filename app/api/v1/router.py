"""
API v1 Router - Main routing configuration
"""
from fastapi import APIRouter
from app.api.v1.endpoints import analyze, ocr

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    analyze.router,
    prefix="/analyze",
    tags=["Code Analysis"]
)

api_router.include_router(
    ocr.router,
    prefix="/ocr",
    tags=["OCR Text Extraction"]
)