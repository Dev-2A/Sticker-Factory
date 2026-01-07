from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("sticker_factory")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    
    # File
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    
    logger.info("Logging initialized: %s", str(log_path))
    return logger