import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from src.config.settings import Settings

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """
    An asynchronous background job scheduler that triggers jobs periodically.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.interval = self.settings.scheduler_interval_seconds
        self.stop_event = asyncio.Event()
        self._current_task: asyncio.Task[None] | None = None

    def start(
        self, job_func: Callable[[], Coroutine[Any, Any, None]]
    ) -> asyncio.Task[None]:
        """
        Starts the scheduler loop in an asyncio task.
        """
        self.stop_event.clear()
        self._current_task = asyncio.create_task(self._run_loop(job_func))
        logger.info(f"Scheduler started. Loop interval: {self.interval} seconds.")
        return self._current_task

    async def stop(self) -> None:
        """
        Gracefully stops the scheduler.
        """
        logger.info("Scheduler stopping...")
        self.stop_event.set()
        if self._current_task and not self._current_task.done():
            # Wait for current sleep or execution to finish cleanly
            await self._current_task
        logger.info("Scheduler stopped.")

    async def _run_loop(
        self, job_func: Callable[[], Coroutine[Any, Any, None]]
    ) -> None:
        """
        Internal loop that executes the job and then sleeps.
        """
        while not self.stop_event.is_set():
            try:
                logger.info("Scheduler triggered job execution.")
                await job_func()
            except Exception as e:
                # Top level catch to ensure the loop never crashes entirely
                logger.critical(
                    f"Scheduler caught unhandled job exception: {e!s}", exc_info=True
                )

            # Sleep until the next interval or until stop is requested
            try:
                # We use asyncio.wait_for to sleep while monitoring the stop_event
                # This allows immediate shutdown even if sleeping for 24 hours.
                await asyncio.wait_for(self.stop_event.wait(), timeout=self.interval)
                # If we get here, the stop_event was set, so we break the loop
                break
            except TimeoutError:
                # Timeout means the interval elapsed normally, so we continue the loop
                continue
