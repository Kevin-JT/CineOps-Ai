import asyncio
import logging
import signal

from src.core.di import Container
from src.core.logger import setup_logger
from src.presentation.scheduler.engine import BackgroundScheduler
from src.presentation.scheduler.jobs import WorkflowJob

logger = logging.getLogger(__name__)


async def run_scheduler() -> None:
    """
    Standalone entrypoint for running the CineOps AI Scheduler.
    """
    container = Container()
    settings = container.settings

    # Initialize logger for standalone script
    setup_logger(name="cineops_scheduler", log_level=settings.log_level)
    logger.info("Initializing CineOps Scheduler...")

    if not settings.scheduler_enabled:
        logger.warning(
            "Scheduler is disabled in configuration. Set SCHEDULER_ENABLED=True."
        )
        return

    job = WorkflowJob(container)
    scheduler = BackgroundScheduler(settings)

    loop = asyncio.get_running_loop()

    # Handle graceful shutdown
    async def shutdown() -> None:
        logger.info("Received shutdown signal. Stopping scheduler cleanly...")
        await scheduler.stop()
        await container.close()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    # Start the loop
    task = scheduler.start(job.execute)

    # Wait for the scheduler to complete (which happens when stopped)
    try:
        await task
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Scheduler process terminated.")


if __name__ == "__main__":
    asyncio.run(run_scheduler())
