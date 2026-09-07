import logging
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(_PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "execution.log")


def get_logger(name: str = "EmpUpdateAutomation") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        fmt = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )

        c_handler = logging.StreamHandler(sys.stdout)
        c_handler.setLevel(logging.INFO)
        c_handler.setFormatter(fmt)
        logger.addHandler(c_handler)

        f_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        f_handler.setLevel(logging.DEBUG)
        f_handler.setFormatter(fmt)
        logger.addHandler(f_handler)

    return logger
