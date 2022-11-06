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


def init(app_name: str, console_log_level: str, log_to_file: Optional[bool] = False,
         file_log_level: Optional[str] = None):
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
        file_logger = logging.FileHandler(f'{app_name}.log')
        file_logger.setFormatter(formatter)
        file_logger.setLevel(level_name_to_level(file_log_level or console_log_level))
        logger.addHandler(file_logger)


def level_name_to_level(level_name: str):
    return _nameToLevel.get(level_name, _nameToLevel['NOTSET'])


def info(message: str, specific_logger: Optional[str] = None):
    if specific_logger:
        logging.getLogger(specific_logger).info(msg=message)
    else:
        logging.info(msg=message)


def debug(message: str, specific_logger: Optional[str] = None):
    if specific_logger:
        logging.getLogger(specific_logger).debug(msg=message)
    else:
        logging.debug(msg=message)


def error(message: str, specific_logger: Optional[str] = None):
    if specific_logger:
        logging.getLogger(specific_logger).error(msg=message)
    else:
        logging.error(msg=message)
