"""
CodeSnap AI - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="CodeSnap AI",
        description="AI-powered code analysis from screenshots",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware - Allow all origins for now
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        return {
            "service": "CodeSnap AI",
            "status": "running",
            "version": "1.0.0",
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        logger.info("Health check endpoint called")
        return {"status": "healthy", "service": "CodeSnap AI"}
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 CodeSnap AI is starting up...")
        logger.info(f"📍 Environment: {'Development' if settings.DEBUG else 'Production'}")
        logger.info(f"🤖 LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )