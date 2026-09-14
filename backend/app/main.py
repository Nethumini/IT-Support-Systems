"""
Main FastAPI application entry point.
AutoOps AI Backend Server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.core.database import init_db
from app.core.logging_config import setup_logging, get_logger
import importlib
from app.api.endpoints import prediction_monitoring
from app.api.endpoints import analytics
# Importing API endpoint modules lazily later so missing optional packages
# (e.g. langchain) won't prevent the app from starting during development.

# Setup logging
setup_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting AutoOps AI Backend...")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Embedding Provider: {settings.embedding_provider}")
    
    # Initialize database
    logger.info("Initializing database...")
    try:
        # Import models to ensure they're registered with Base
        from app.models.ticket import TicketDB
        from app.models.user import UserDB
        from app.models.chat_history import ChatMessageDB
        from app.models.audit_log import AuditLogDB
        
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    logger.info("AutoOps AI Backend is ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AutoOps AI Backend...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered IT Operations and Support System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "AutoOps AI Backend is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "it-support-systems-backend"
    }


# Include routers (imported lazily below)

# Always try to include lightweight endpoints first (so health/status remain available)
try:
    from app.api.endpoints import status
    app.include_router(
        status.router,
        prefix=f"{settings.api_prefix}",
        tags=["Status"]
    )
    app.include_router(prediction_monitoring.router, 
                       prefix=f"{settings.api_prefix}/prediction_monitoring")
except Exception as e:
    logger.warning(f"Could not include status endpoint at startup: {e}")

# Import other endpoints individually so optional heavy dependencies don't break startup
# Use chat_enhanced (LLM-First with intelligent RAG) for the main chat
for _name, _tag in (("auth", "Authentication"), ("chat_enhanced", "Chat"), ("tickets", "Tickets"), ("dashboard", "Dashboard"), ("monitoring", "Monitoring"),("admin", "Admin"), ("prediction_monitoring", "Predictions"), ("actions", "Actions"), ("analytics", "Analytics")):
    try:
        mod = importlib.import_module(f"app.api.endpoints.{_name}")
        # Monitoring endpoint gets its own prefix path
        if _name == "monitoring":
            app.include_router(
                mod.router,
                prefix=f"{settings.api_prefix}/monitoring",
                tags=[_tag]
            )
        elif _name == "admin":
            app.include_router(
                mod.router,
                prefix=f"{settings.api_prefix}/admin",
                tags=[_tag]
            )
        elif _name == "analytics":
            app.include_router(
                mod.router,
                prefix=f"{settings.api_prefix}/analytics",
                tags=[_tag]
            )
        else:
            app.include_router(
                mod.router,
                prefix=f"{settings.api_prefix}",
                tags=[_tag]
            )
    except Exception as e:
        logger.warning(f"Could not include {_name} endpoint at startup: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
