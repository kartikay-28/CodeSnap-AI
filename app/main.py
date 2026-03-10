"""
CodeSnap AI - Main FastAPI Application
Production-ready backend with CORS, health checks, and keep-alive
"""
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
import logging
import asyncio
import httpx
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keep-alive task reference
keep_alive_task = None


async def keep_alive_ping():
    """Background task to ping health endpoint every 10 minutes to keep Render instance active"""
    await asyncio.sleep(60)  # Wait 1 minute before starting
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Ping own health endpoint
                response = await client.get("http://localhost:8000/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info("✅ Keep-alive ping successful")
                else:
                    logger.warning(f"⚠️ Keep-alive ping returned status {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Keep-alive ping failed: {str(e)}")
            
            # Wait 10 minutes before next ping
            await asyncio.sleep(600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("🚀 CodeSnap AI is starting up...")
    logger.info(f"📍 Environment: {'Development' if settings.DEBUG else 'Production'}")
    logger.info(f"🤖 LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    
    # Start keep-alive background task
    global keep_alive_task
    keep_alive_task = asyncio.create_task(keep_alive_ping())
    logger.info("⏰ Keep-alive task started (10-minute interval)")
    
    yield
    
    # Shutdown
    logger.info("🛑 CodeSnap AI is shutting down...")
    if keep_alive_task:
        keep_alive_task.cancel()
        try:
            await keep_alive_task
        except asyncio.CancelledError:
            logger.info("✅ Keep-alive task cancelled")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="CodeSnap AI",
        description="AI-powered code analysis from screenshots",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS middleware - MUST be added before routes
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://codesnap-ai-28.netlify.app",  # Production frontend
            "http://localhost:3000",                # Local development
            "http://localhost:5500",                # Live Server
            "http://127.0.0.1:3000",               # Local development
            "http://127.0.0.1:5500",               # Live Server
            "*"                                     # Allow all during development
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
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
        """Health check endpoint for monitoring and keep-alive"""
        return {
            "status": "healthy",
            "service": "CodeSnap AI"
        }
    
    # Favicon handler to prevent 404 errors
    @app.get("/favicon.ico")
    async def favicon():
        """Return empty response for favicon to prevent 404 logs"""
        return Response(content="", media_type="image/x-icon")
    
    # Include API routes
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