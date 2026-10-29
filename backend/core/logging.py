"""Structured application logging for WealthOS AI."""

import logging
import sys
from backend.core.config import settings

def setup_logging():
    log_level = getattr(logging, settings.ENVIRONMENT.upper() == "PRODUCTION" and "INFO" or "DEBUG", logging.INFO)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Avoid duplicate handlers if re-called
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers[0] = handler

    logger = logging.getLogger("wealthos")
    return logger

logger = setup_logging()
