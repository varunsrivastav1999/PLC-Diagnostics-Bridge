from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.api.routes import plc
from app.core.config import settings
from app.core.logger import setup_logging
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError, PLCTimeoutError
from app.utils.connection_cache import connection_cache
import logging

# Initialize structured logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting")
    yield
    logger.info("Shutting down — closing all PLC connections")
    connection_cache.clear_all()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(PLCConnectionError)
async def plc_connection_error_handler(request: Request, exc: PLCConnectionError):
    logger.error(f"Connection error: {exc}")
    return JSONResponse(status_code=200, content={
        "success": False, "message": str(exc), "value": None, "connected": False,
        "timestamp": None
    })

@app.exception_handler(PLCReadError)
async def plc_read_error_handler(request: Request, exc: PLCReadError):
    logger.error(f"Read error: {exc}")
    return JSONResponse(status_code=200, content={
        "success": False, "message": str(exc), "value": None, "connected": True,
        "timestamp": None
    })

@app.exception_handler(PLCWriteError)
async def plc_write_error_handler(request: Request, exc: PLCWriteError):
    logger.error(f"Write error: {exc}")
    return JSONResponse(status_code=200, content={
        "success": False, "message": str(exc), "value": None, "connected": True,
        "timestamp": None
    })

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url.path}")
    return JSONResponse(status_code=500, content={
        "success": False, "message": "Internal server error", "value": None,
        "connected": False, "timestamp": None
    })

# Routes
app.include_router(plc.router, prefix="/api/plc", tags=["PLC Operations"])

# Lifecycle now managed via lifespan context manager

# Health
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "version": settings.VERSION}
