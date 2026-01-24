"""
Main FastAPI application.
Entry point for the PronIELTS backend API.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="IELTS Pronunciation Assessment Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Returns basic information about the API status.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME,
        "mock_mode": settings.MOCK_MODE,
    }


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.

    Logs important configuration information when the application starts.
    """
    logger.info("=" * 60)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info("=" * 60)
    logger.info(f"Mock Mode: {settings.MOCK_MODE}")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    logger.info(f"CORS Origins: {settings.cors_origins_list}")

    if settings.MOCK_MODE:
        logger.info("ℹ️  Running in MOCK MODE - using mock Azure services")
        logger.info("ℹ️  Speech assessments will return randomized scores")
        logger.info("ℹ️  Audio files will be saved to ./mock_blob_storage/")
    else:
        logger.info("☁️  Running in AZURE MODE - using real Azure services")
        logger.info(f"☁️  Speech Region: {settings.SPEECH_REGION}")

    logger.info("=" * 60)
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/health")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.

    Logs when the application is shutting down.
    """
    logger.info("Shutting down PronIELTS API...")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return {"detail": "Resource not found", "status_code": 404}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    logger.error(f"Internal server error: {str(exc)}", exc_info=True)
    return {"detail": "Internal server error. Please try again later.", "status_code": 500}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
