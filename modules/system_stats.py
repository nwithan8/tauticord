import enum
import os
import shutil

import psutil

from modules import utils


class CPUTimeFrame(enum.Enum):
    INSTANT = 0
    ONE_MINUTE = 1
    FIVE_MINUTES = 5
    FIFTEEN_MINUTES = 15


def cpu_usage(timeframe: CPUTimeFrame = CPUTimeFrame.INSTANT) -> float:
    """
    Get the current CPU usage percentage

    :param timeframe: (Optional) Timeframe to get CPU usage for
    :type timeframe: CPUTimeFrame, optional
    :return: CPU usage percentage
    :rtype: float
    """
    match timeframe:
        case CPUTimeFrame.INSTANT:
            return psutil.cpu_percent(interval=1)  # 1 second
        case CPUTimeFrame.ONE_MINUTE:
            load, _, _ = psutil.getloadavg()
            return load / os.cpu_count() * 100
        case CPUTimeFrame.FIVE_MINUTES:
            _, load, _ = psutil.getloadavg()
            return load / os.cpu_count() * 100
        case CPUTimeFrame.FIFTEEN_MINUTES:
            _, _, load = psutil.getloadavg()
            return load / os.cpu_count() * 100
        case _:
            raise ValueError("Invalid timeframe")


def cpu_usage_display(timeframe: CPUTimeFrame = CPUTimeFrame.INSTANT) -> str:
    """
    Get the current CPU usage display

    :param timeframe: (Optional) Timeframe to get CPU usage for
    :type timeframe: CPUTimeFrame, optional
    :return: CPU usage display
    :rtype: str
    """
    return f"{utils.format_decimal(cpu_usage(timeframe))}%"


def ram_usage_percentage() -> float:
    """
    Get the current RAM usage percentage

    :return: RAM usage percentage
    :rtype: float
    """
    return psutil.virtual_memory()[2]


def ram_usage() -> float:
    """
    Get the current RAM usage in GB

    :return: RAM usage in GB
    :rtype: float
    """
    return psutil.virtual_memory()[3] / 1000000000


def ram_usage_display() -> str:
    """
    Get the current RAM usage display

    :return: RAM usage display
    :rtype: str
    """
    return f"{utils.format_decimal(ram_usage())} GB ({utils.format_decimal(ram_usage_percentage())}%)"


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
