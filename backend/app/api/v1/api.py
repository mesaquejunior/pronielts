"""API v1 router - combines all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import assessments, categories, dialogs, phrases, users

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])

api_router.include_router(categories.router, tags=["categories"])

api_router.include_router(dialogs.router, tags=["dialogs"])

api_router.include_router(phrases.router, tags=["phrases"])

api_router.include_router(users.router, prefix="/users", tags=["users"])
