from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel

from src.application.services.coordinator import WorkflowCoordinator
from src.presentation.api.dependencies import get_coordinator

router = APIRouter(prefix="/workflow", tags=["workflow"])


class WorkflowResponse(BaseModel):
    status: str
    message: str


@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(
    background_tasks: BackgroundTasks,
    coordinator: WorkflowCoordinator = Depends(get_coordinator),
) -> WorkflowResponse:
    """
    Triggers the end-to-end recommendation workflow asynchronously in the background.
    """
    background_tasks.add_task(coordinator.run_pipeline)
    return WorkflowResponse(
        status="accepted",
        message="Workflow triggered and is running in the background.",
    )
