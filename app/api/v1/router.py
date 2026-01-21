"""
API v1 Router - Main routing configuration
"""
from fastapi import APIRouter
from app.api.v1.endpoints import analyze

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    analyze.router,
    prefix="/analyze",
    tags=["Code Analysis"]
)