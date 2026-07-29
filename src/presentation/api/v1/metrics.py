from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/metrics", tags=["metrics"])


class MetricsResponse(BaseModel):
    status: str


@router.get("", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """
    Placeholder for prometheus/custom metrics.
    """
    return MetricsResponse(status="not_implemented")
