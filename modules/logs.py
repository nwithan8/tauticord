import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

from pytz import timezone

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
MAX_SIZE = 5000000  # 5 MB
MAX_FILES = 5


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
    timezone_abbr = os.getenv('TZ',
                              'UTC')  # Due to chicken-egg issue, we can't parse the timezone from config, only from env
    formatter.converter = lambda *args: datetime.now(tz=timezone(timezone_abbr)).timetuple()

    # Console logging
    console_logger = logging.StreamHandler()
    console_logger.setFormatter(formatter)
    console_logger.setLevel(level_name_to_level(console_log_level))
    logger.addHandler(console_logger)

    # File logging
    if log_to_file:
        log_file_dir = log_file_dir if log_file_dir.endswith('/') else f'{log_file_dir}/'
        try:
            os.makedirs(log_file_dir)
        except:
            pass
        file_logger = RotatingFileHandler(filename=f'{log_file_dir}{app_name}.log',
                                          maxBytes=MAX_SIZE, backupCount=MAX_FILES, encoding='utf-8')
        file_logger.setFormatter(formatter)
        file_logger.setLevel(level_name_to_level(file_log_level or console_log_level))
        logger.addHandler(file_logger)


def level_name_to_level(level_name: str):
    return _nameToLevel.get(level_name, _nameToLevel['NOTSET'])


def warning(message: str, specific_logger: Optional[str] = None):
    logging.getLogger(specific_logger if specific_logger else _DEFAULT_LOGGER_NAME).warning(msg=message)


def info(message: str, specific_logger: Optional[str] = None):
    logging.getLogger(specific_logger if specific_logger else _DEFAULT_LOGGER_NAME).info(msg=message)


def debug(message: str, specific_logger: Optional[str] = None):
    logging.getLogger(specific_logger if specific_logger else _DEFAULT_LOGGER_NAME).debug(msg=message)


def error(message: str, specific_logger: Optional[str] = None):
    logging.getLogger(specific_logger if specific_logger else _DEFAULT_LOGGER_NAME).error(msg=message)


def critical(message: str, specific_logger: Optional[str] = None):
    logging.getLogger(specific_logger if specific_logger else _DEFAULT_LOGGER_NAME).critical(msg=message)


def fatal(message: str, specific_logger: Optional[str] = None):
    logging.getLogger(specific_logger if specific_logger else _DEFAULT_LOGGER_NAME).critical(msg=message)
