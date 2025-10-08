from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import settings
from .core.redis_client import redis_client
from .core.logging_config import conversation_logger
from .api import conversations, websockets, personas, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await redis_client.connect()
    # Log system startup (using a dummy conversation_id for system events)
    conversation_logger.log_event("system", "fastapi_startup", {
        "version": "1.0.0",
        "environment": "development",
        "features": ["multi_ai_conversation", "persona_creator", "advanced_logging"]
    })
    yield
    # Shutdown
    await redis_client.disconnect()
    conversation_logger.log_event("system", "fastapi_shutdown", {
        "reason": "application_shutdown"
    })

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(conversations.router, prefix="/api")
app.include_router(personas.router, prefix="/api")
app.include_router(websockets.router, prefix="/ws")

@app.get("/")
async def root():
    return {"message": "Chimera Multi-AI Chat API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}