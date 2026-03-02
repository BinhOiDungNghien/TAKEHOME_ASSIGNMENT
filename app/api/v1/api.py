from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

# Grouping all v1 endpoints under appropriate routers
api_router.include_router(health.router, tags=["Health"])
