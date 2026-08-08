import asyncio
import sys

from src.core.di import Container
from src.core.logger import setup_logger

logger = setup_logger("cineops.run_daily")


async def run_daily_workflow() -> None:
    """
    Instantiates the DI container, runs the recommendation workflow once,
    and cleanly shuts down. Designed for scheduled tasks (e.g., GitHub Actions).
    """
    logger.info("Initializing DI container for daily workflow...")
    container = Container()

    try:
        logger.info("Starting the pipeline...")
        await container.coordinator.run_pipeline()
        logger.info("Pipeline executed successfully.")
    except Exception as e:
        logger.critical(f"Daily workflow failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Closing DI container and freeing resources...")
        await container.close()
        logger.info("Shutdown complete.")


def main() -> None:
    """
    Entry point for the daily script.
    """
    asyncio.run(run_daily_workflow())


if __name__ == "__main__":
    main()
