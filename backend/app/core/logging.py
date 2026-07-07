from __future__ import annotations

import logging
import sys

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(level: str) -> None:
    normalized_level = level.upper()
    root_logger = logging.getLogger()
    root_logger.setLevel(normalized_level)

    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        root_logger.addHandler(handler)

    logging.getLogger("genforge").setLevel(normalized_level)
