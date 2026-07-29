import asyncio
import sys

from src.config.settings import get_settings
from src.core.di import Container
from src.core.logger import setup_logger
from src.core.utils import ensure_directory


async def main() -> None:
    """
    Main application entry point.
    """
    # 1. Bootstrapping
    settings = get_settings()

    # Ensure data directory exists
    ensure_directory(settings.data_directory)

    logger = setup_logger(
        name="cineops",
        log_level=settings.log_level,
    )

    logger.info("Starting CineOps AI Application...")
    logger.info(f"Environment: {settings.app_env.value}")

    # 2. Dependency Injection Initialization
    try:
        _ = Container()
        logger.info("Dependency Injection container initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize container: {e}", exc_info=True)
        sys.exit(1)

    # 3. Execution Pipeline (Placeholder)
    try:
        logger.info("Executing recommendation pipeline...")
        # pipeline = container.recommendation_pipeline
        # await pipeline.execute()

        # Simulate some work
        await asyncio.sleep(1)
        logger.info("Pipeline execution completed successfully.")

    except Exception:
        logger.exception("Pipeline execution failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
