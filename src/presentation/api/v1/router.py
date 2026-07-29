from fastapi import APIRouter, Depends

from src.presentation.api.dependencies import verify_api_key
from src.presentation.api.v1.captions import router as captions_router
from src.presentation.api.v1.hashtags import router as hashtags_router
from src.presentation.api.v1.health import router as health_router
from src.presentation.api.v1.metrics import router as metrics_router
from src.presentation.api.v1.recommendations import router as recommendations_router
from src.presentation.api.v1.workflow import router as workflow_router

api_router = APIRouter()

# Public endpoints
api_router.include_router(health_router)
api_router.include_router(metrics_router)

# Protected endpoints
api_router.include_router(
    recommendations_router, dependencies=[Depends(verify_api_key)]
)
api_router.include_router(captions_router, dependencies=[Depends(verify_api_key)])
api_router.include_router(hashtags_router, dependencies=[Depends(verify_api_key)])
api_router.include_router(workflow_router, dependencies=[Depends(verify_api_key)])
