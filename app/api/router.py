from fastapi import APIRouter

from app.api.routes.events import router as events_router
from app.api.routes.favorite_recipe import router as favorite_recipe_router
from app.api.routes.health import router as health_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.recognition import router as recognition_router
from app.api.routes.recommendation import router as recommendation_router
from app.api.routes.scan import router as scan_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(recognition_router)
api_router.include_router(inventory_router)
api_router.include_router(events_router)
api_router.include_router(recommendation_router)
api_router.include_router(scan_router)
api_router.include_router(favorite_recipe_router)
