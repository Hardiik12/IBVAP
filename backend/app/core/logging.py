import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configures application-wide structured logging.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Silence overly verbose third-party loggers if necessary
    logging.getLogger("uvicorn.access").setLevel(log_level)


logger = logging.getLogger("ibvap.backend")
