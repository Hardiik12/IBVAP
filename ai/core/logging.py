import logging
import sys
from ai.core.config import ai_settings


def setup_ai_logging() -> None:
    """
    Configure structured logging for the AI module.
    """
    log_level = getattr(logging, ai_settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] [%(levelname)s] [ibvap.ai.%(module)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


setup_ai_logging()
