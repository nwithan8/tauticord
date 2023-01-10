import logging
from typing import Optional

_nameToLevel = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}

_DEFAULT_LOGGER_NAME = None

def init(app_name: str,
         console_log_level: str,
         log_to_file: Optional[bool] = False,
         log_file_dir: Optional[str] = "",
         file_log_level: Optional[str] = None):
    global _DEFAULT_LOGGER_NAME
    _DEFAULT_LOGGER_NAME = app_name

    logger = logging.getLogger(app_name)

    # Default log to DEBUG
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - [%(levelname)s]: %(message)s')

    # Console logging
    console_logger = logging.StreamHandler()
    console_logger.setFormatter(formatter)
    console_logger.setLevel(level_name_to_level(console_log_level))
    logger.addHandler(console_logger)

    # File logging
    if log_to_file:
        file_logger = logging.FileHandler(f'{log_file_dir}{app_name}.log')
        file_logger.setFormatter(formatter)
        file_logger.setLevel(level_name_to_level(file_log_level or console_log_level))
        logger.addHandler(file_logger)


def level_name_to_level(level_name: str):
    return _nameToLevel.get(level_name, _nameToLevel['NOTSET'])


def info(message: str, specific_logger: Optional[str] = None):
    logging.getLogger(specific_logger if specific_logger else _DEFAULT_LOGGER_NAME).info(msg=message)


def debug(message: str, specific_logger: Optional[str] = None):
    logging.getLogger(specific_logger if specific_logger else _DEFAULT_LOGGER_NAME).debug(msg=message)


def error(message: str, specific_logger: Optional[str] = None):
    logging.getLogger(specific_logger if specific_logger else _DEFAULT_LOGGER_NAME).error(msg=message)
