"""
CodeSnap AI - Main FastAPI Application
Production-ready backend with CORS and health checks
"""
from fastapi import FastAPI, Response, Request
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
    
    # CORS middleware - MUST be added FIRST before any routes
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600
    )
    
    @app.middleware("http")
    async def add_cors_headers(request: Request, call_next):
        """Add CORS headers to all responses"""
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 CodeSnap AI is starting up...")
        logger.info(f"📍 Environment: {'Development' if settings.DEBUG else 'Production'}")
        logger.info(f"🤖 LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
        logger.info("✅ CORS enabled for all origins")
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with service information"""
        return {
            "service": "CodeSnap AI",
            "status": "running",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1"
        }
    
    # Health check endpoint
    @app.get("/health")
    @app.head("/health")
    async def health_check():
        """Health check endpoint for monitoring"""
        return {
            "status": "healthy",
            "service": "CodeSnap AI"
        }
    
    # Favicon handler to prevent 404 errors
    @app.get("/favicon.ico")
    async def favicon():
        """Return empty response for favicon to prevent 404 logs"""
        return Response(content="", media_type="image/x-icon")
    
    # Include API routes AFTER middleware
    app.include_router(api_router, prefix="/api/v1")
    
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