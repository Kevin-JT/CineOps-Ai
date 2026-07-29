import logging
import time

from src.core.di import Container
from src.core.exceptions import CineOpsError
from src.core.retry import async_retry

logger = logging.getLogger(__name__)


class WorkflowJob:
    """
    Background job that wraps the WorkflowCoordinator to add job-level resiliency,
    telemetry, and logging.
    """

    def __init__(self, container: Container) -> None:
        self.coordinator = container.coordinator

    @async_retry(
        max_attempts=3,
        base_delay=10.0,
        max_delay=60.0,
        exceptions=(Exception,),
        raise_exc=CineOpsError,
    )
    async def execute(self) -> None:
        """
        Executes the CineOps AI workflow with retries and produces an execution summary.
        """
        import uuid

        from src.core.context import execution_id_ctx

        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        token = execution_id_ctx.set(execution_id)

        try:
            logger.info("--- [JOB START] CineOps Workflow ---")
            start_time = time.perf_counter()

            try:
                await self.coordinator.run_pipeline()
                elapsed = time.perf_counter() - start_time
                logger.info(f"--- [JOB SUCCESS] Completed in {elapsed:.2f}s ---")
            except Exception as e:
                elapsed = time.perf_counter() - start_time
                logger.error(f"--- [JOB FAILED] Failed after {elapsed:.2f}s: {e!s} ---")
                # We re-raise to trigger the @async_retry decorator logic
                raise
        finally:
            execution_id_ctx.reset(token)
