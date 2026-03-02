from fastapi import APIRouter
from app.api.v1.endpoints import health, sessions, chat

api_router = APIRouter()

# Grouping all v1 endpoints under appropriate routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
