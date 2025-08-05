from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Agentic Chat Assistant API...")
    logger.info(f"Version: {settings.VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize components
    try:
        # Import to initialize global instances
        from app.agents.tool_registry import tool_registry
        from app.agents.intent_classifier import intent_classifier
        from app.agents.agent_orchestrator import agent_orchestrator
        
        logger.info("Agent system initialized successfully")
        
        # Check OpenAI configuration
        if settings.OPENAI_API_KEY:
            logger.info("OpenAI API key configured")
        else:
            logger.warning("OpenAI API key not configured - some features may be limited")
        
        # Log available tools
        tools = tool_registry.get_enabled_tools()
        logger.info(f"Loaded {len(tools)} tools: {list(tools.keys())}")
        
    except Exception as e:
        logger.error(f"Failed to initialize agent system: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agentic Chat Assistant API...")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="An intelligent agentic chat assistant that routes queries to specialized tools",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "type": type(exc).__name__
        }
    )

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Agentic Chat Assistant API",
        "status": "operational",
        "docs": "/docs",
        "api": settings.API_V1_STR
    }

# Health check endpoint (also available at root level)
@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "healthy", "version": settings.VERSION}

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
