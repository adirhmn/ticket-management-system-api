import logging
import sys
import time
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.logging_config import JsonFormatter

# Configure root logger to output structured JSON logs to stdout
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(JsonFormatter())
logging.getLogger().handlers = [log_handler]
logging.getLogger().setLevel(logging.INFO)

# Instantiate API logger
logger = logging.getLogger("api")


from app.database import engine, Base
from app.config import settings
from app.routers import health, tickets



app = FastAPI(
    title="Contact Center Support Tickets API",
    description="A production-ready FastAPI backend for managing support tickets with authentication, search, and pagination.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
allowed_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom error handler for Request Validation Errors (e.g., Pydantic schema validation failures)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler to clean up and structure Pydantic validation errors.
    This provides clear feedback for email format, enum values, and string length failures.
    """
    errors = []
    for error in exc.errors():
        loc = " -> ".join([str(x) for x in error.get("loc", [])])
        msg = error.get("msg")
        errors.append({
            "field": loc,
            "error": msg,
            "type": error.get("type")
        })
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "validation_error",
            "message": "One or more fields failed validation checks.",
            "details": errors
        }
    )

# Custom error handler for standard HTTPExceptions (like 404 Not Found, 401 Unauthorized)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom exception handler to conform HTTPExceptions to the generic ApiResponse format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None
        }
    )

# Catch-all error handler for unhandled internal server exceptions (500 errors)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler to intercept all uncaught exceptions (500 Internal Server Errors).
    Ensures the client receives a structured JSON response instead of a raw traceback or HTML.
    """
    # Log the critical error with complete traceback details inside the structured JSON log
    logger.error(f"Unhandled server exception: {str(exc)}", exc_info=exc)

    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected internal server error occurred.",
            "data": None
        }
    )


# Middleware for request logging and timing
@app.middleware("http")
async def log_requests_and_timing(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    duration_ms = (time.time() - start_time) * 1000
    
    # Add timing header to response
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
    
    # Generate structured JSON log
    logger.info(
        f"Request {request.method} {request.url.path} completed with status {response.status_code}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    return response


# Mount routers
app.include_router(health.router)
app.include_router(tickets.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Ticket Management System API. Go to /docs for the Swagger interactive API documentation.",
        "health_check": "/health",
        "docs": "/docs"
    }
