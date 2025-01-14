import functools
import logging
import os
from contextlib import contextmanager
from logging.handlers import SysLogHandler
from time import perf_counter_ns
import json

from constants import LOGGER_NAME


# я ни хрена не понимаю как это работает, но оно работает
def timer_decorator(logger):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            pf_start = perf_counter_ns()
            result = func(*args, **kwargs)
            pf_end = perf_counter_ns()
            logger.info(f"Execution of {func.__name__} took {(pf_end-pf_start)/1000000} ms")
            return result
        return wrapper
    return decorator

@contextmanager
def timer(logger, descriptor):
    pf_start = perf_counter_ns()
    try:
        yield
    finally:
        # Внутри вызова __exit__
        pf_end = perf_counter_ns()
        logger.info(f"Execution of {descriptor} took {(pf_end - pf_start) / 1000000} ms")

def setup_logger(level=logging.INFO):
    env_level = os.environ.get('LOGGING.LEVEL')
    # пытаемся взять уровень логирования из ENV
    if env_level is None or env_level not in logging._nameToLevel.keys():
        print(f"ENV named LOGGING.LEVEL not set or bad, level {logging.getLevelName(level)} applied")
    else:
        level = env_level

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    handlers = []
    # Create handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # консоль у всех
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    is_docker = os.environ.get('DOCKER_ENV', False)
    if is_docker:
        syslog_handler = SysLogHandler()
        syslog_handler.setFormatter(formatter)
        handlers.append(syslog_handler)
    else:
        file_handler = logging.FileHandler(f"./logs/{LOGGER_NAME}.log")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    # Create formatters and add them to handlers

    # Add handlers to the logger
    for h in handlers:
        logger.addHandler(h)
    return logger

