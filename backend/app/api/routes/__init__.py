from fastapi import APIRouter
from app.api.routes import health, analysis

router = APIRouter()

router.include_router(health.router)
router.include_router(analysis.router)
