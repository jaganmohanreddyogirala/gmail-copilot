import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Tuple
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.routes import router as api_router
from app.models.db import init_db, engine
from app.core.logging import setup_structured_logging

setup_structured_logging()
logger = logging.getLogger("gmail_copilot")

# Rate limiting sliding window tracking (IP -> list of timestamps)
RATE_LIMIT_STORE: Dict[str, Dict[str, list]] = {}
RATE_LIMIT_RULES = {
    "default": (100, 60),  # 100 requests per 60 seconds
    "process": (10, 60),   # 10 processing requests per 60 seconds
    "eval": (3, 60),       # 3 benchmark eval triggers per 60 seconds
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Gmail Copilot API backend (Production Hardened)...")
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization skipped or fallback active: {e}")
    yield
    logger.info("Shutting down Gmail Copilot API backend...")


app = FastAPI(
    title="Gmail Copilot API",
    description="Production-Grade AI Email Agent powered by FastAPI, LangGraph, RAG & MCP Tools",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url=None,
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# Rate Limiting Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if not settings.RATE_LIMIT_ENABLED:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    now = time.time()

    rule_key = "default"
    if "/process" in path:
        rule_key = "process"
    elif "/eval/run" in path:
        rule_key = "eval"

    max_reqs, window_sec = RATE_LIMIT_RULES[rule_key]

    if client_ip not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[client_ip] = {}
    if rule_key not in RATE_LIMIT_STORE[client_ip]:
        RATE_LIMIT_STORE[client_ip][rule_key] = []

    # Clean old timestamps outside window
    timestamps = [t for t in RATE_LIMIT_STORE[client_ip][rule_key] if now - t < window_sec]
    RATE_LIMIT_STORE[client_ip][rule_key] = timestamps

    if len(timestamps) >= max_reqs:
        logger.warning(f"Rate limit exceeded for IP {client_ip} on {path} ({rule_key})")
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
        )

    RATE_LIMIT_STORE[client_ip][rule_key].append(now)
    return await call_next(request)


# Safe Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    detail = "An internal server error occurred." if settings.APP_ENV == "production" else str(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": detail},
    )


# Explicit CORS Origins for Production
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", summary="Root Endpoint")
def read_root():
    return {
        "app": "Gmail Copilot API",
        "version": "2.0.0",
        "status": "running",
        "environment": settings.APP_ENV,
        "docs": "/docs",
        "auth_status": "/auth/status",
    }


@app.get("/health", summary="Liveness Health Check")
def health_check():

    """Liveness probe: verifies application server is running."""
    return {
        "status": "healthy",
        "app": "Gmail Copilot API",
        "version": "2.0.0",
        "environment": settings.APP_ENV,
        "timestamp": time.time(),
    }


@app.get("/ready", summary="Readiness Check")
async def readiness_check():
    """Readiness probe: verifies database connectivity and configuration state."""
    db_ready = True
    try:
        async with engine.connect() as conn:
            pass
    except Exception as e:
        logger.warning(f"Readiness check DB query failed: {e}")
        db_ready = False

    auth_configured = bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    return {
        "status": "ready" if db_ready else "degraded",
        "database_ready": db_ready,
        "auth_configured": auth_configured,
        "rate_limiting_enabled": settings.RATE_LIMIT_ENABLED,
        "auth_middleware_enabled": settings.ENABLE_AUTH,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
