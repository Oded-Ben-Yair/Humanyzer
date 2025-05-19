"""
API routes package.
"""
from fastapi import APIRouter
from backend.api.routes.transform import router as transform_router

router = APIRouter()

# Include all route modules
router.include_router(transform_router, prefix="/transform", tags=["transform"])

# Add more routers as needed
