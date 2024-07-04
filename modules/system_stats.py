import os
import shutil

from modules import utils


def path_exists(path: str) -> bool:
    """
    Check if a path exists

    :param path: Path to check
    :type path: str
    :return: True if path exists, False if not
    :rtype: bool
    """
    return os.path.exists(path)


def disk_space_info(path: str) -> tuple:
    """
    Get the current disk usage total, used, and free in bytes

    :param path: Path to get disk usage for
    :type path: str
    :return: Disk usage total, used, and free in bytes
    :rtype: tuple
    """
    total, used, free = shutil.disk_usage(path)
    return total, used, free


def disk_usage_display(path: str) -> str:
    """
    Get the current disk usage display

    :param path: Path to get disk usage for
    :type path: str
    :return: Disk usage display
    :rtype: str
    """
    total, used, free = disk_space_info(path)

    space_used = utils.human_size(used, decimal_places=1, no_zeros=True)
    total_space = utils.human_size(total, decimal_places=1, no_zeros=True)
    percentage_used = utils.format_decimal(used / total * 100, decimal_places=2, no_zeros=True)

    return f"{space_used}/{total_space} ({percentage_used}%)"
