import enum

import psutil
import os

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
            return psutil.cpu_percent(interval=1) # 1 second
        case CPUTimeFrame.ONE_MINUTE:
            load, _, _ = psutil.getloadavg()
            return load/os.cpu_count() * 100
        case CPUTimeFrame.FIVE_MINUTES:
            _, load, _ = psutil.getloadavg()
            return load/os.cpu_count() * 100
        case CPUTimeFrame.FIFTEEN_MINUTES:
            _, _, load = psutil.getloadavg()
            return load/os.cpu_count() * 100
        case _:
            raise ValueError("Invalid timeframe")

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
    return psutil.virtual_memory()[3]/1000000000
