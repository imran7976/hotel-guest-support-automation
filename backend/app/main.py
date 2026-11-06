from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.v1.api import api_router
from app.database.session import SessionLocal
from app.database.seed_data import init_db

# Initialize logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables and initial seed data exist
    logger.info("Initializing Hotel Guest Support Backend...")
    db = SessionLocal()
    try:
        init_db(db)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error during startup DB initialization: {e}", exc_info=True)
    finally:
        db.close()
    
    yield
    logger.info("Shutting down Hotel Guest Support Backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Professional AI-Powered Hotel Guest Support Automation Platform integrating FastAPI, OpenAI, RAG, n8n, and MySQL.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     response = await call_next(request)
#     response.headers["X-Hotel-System"] = "GrandAzure-AI-Automation-v1"
#     return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred while processing the hotel guest request."}
    )


# Health check endpoints
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "docs_url": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ai_model": settings.OPENAI_MODEL_NAME,
        "n8n_integration": "enabled" if settings.N8N_ENABLED else "disabled"
    }


# Mount API V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
