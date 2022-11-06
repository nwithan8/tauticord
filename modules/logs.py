import logging

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

def init(log_level_name: str):
    logging.basicConfig(format='%(asctime)s - [%(levelname)s]: %(message)s', level=level_name_to_level(level_name=log_level_name))

def level_name_to_level(level_name: str):
    return _nameToLevel.get(level_name, _nameToLevel['NOTSET'])


def info(message):
    logging.info(msg=message)


def debug(message):
    logging.debug(msg=message)


def error(message):
    logging.error(msg=message)
