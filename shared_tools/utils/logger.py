import logging
import sys
from datetime import datetime


class CustomLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                fmt="[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, msg: str, *args):
        self.logger.info(msg, *args)

    def warn(self, msg: str, *args):
        self.logger.warning(msg, *args)

    def error(self, msg: str, *args):
        self.logger.error(msg, *args)

    def step(self, step_num: int, description: str):
        self.logger.info(f"--- [STEP {step_num}] {description} ---")


def get_logger(name: str) -> CustomLogger:
    return CustomLogger(name)
