from datetime import datetime, timedelta


def make_plural(word, count: int, suffix_override: str = 's'):
    if count > 1:
        return f"{word}{suffix_override}"
    return word


def human_bitrate(B, d=1):
    # 'Return the given kilobytes as a human friendly Kbps, Mbps, Gbps, or Tbps string'
    # Next line altered so that this takes in kilobytes instead of bytes, as it was originally written
    B = float(B) * 1024
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if d <= 0:
        if B < KB:
            return f'{B} bps'
        elif KB <= B < MB:
            return f'{int(B / KB):d} kbps'
        elif MB <= B < GB:
            return f'{int(B / MB):d} Mbps'
        elif GB <= B < TB:
            return f'{int(B / GB):d} Gbps'
        elif TB <= B:
            return f'{int(B / TB):d} Tbps'
    else:
        if B < KB:
            return f'{B} bps'
        elif KB <= B < MB:
            return f'{int(B / KB):.{d}} kbps'
        elif MB <= B < GB:
            return f'{int(B / MB):.{d}f} Mbps'
        elif GB <= B < TB:
            return f'{int(B / GB):.{d}f} Gbps'
        elif TB <= B:
            return f'{int(B / TB):.{d}f} Tbps'


def milliseconds_to_minutes_seconds(milliseconds: int):
    seconds = int(milliseconds / 1000)
    minutes = int(seconds / 60)
    if minutes < 10:
        minutes = f"0{minutes}"
    seconds = int(seconds % 60)
    if seconds < 10:
        seconds = f"0{seconds}"
    return f"{minutes}:{seconds}"


def now_plus_milliseconds(milliseconds: int):
    now = datetime.now()
    return now + timedelta(milliseconds=milliseconds)


def string_to_datetime(date_string: str, template: str = "%Y-%m-%dT%H:%M:%S") -> datetime:
    """
    Convert a datetime string to a datetime.datetime object

    :param date_string: datetime string to convert
    :type date_string: str
    :param template: (Optional) datetime template to use when parsing string
    :type template: str, optional
    :return: datetime.datetime object
    :rtype: datetime.datetime
    """
    if date_string.endswith('Z'):
        date_string = date_string[:-5]
    return datetime.strptime(date_string, template)


def datetime_to_string(datetime_object: datetime, template: str = "%Y-%m-%dT%H:%M:%S.000Z") -> str:
    """
    Convert a datetime.datetime object to a string

    :param datetime_object: datetime.datetime object to convert
    :type datetime_object: datetime.datetime
    :param template: (Optional) datetime template to use when parsing string
    :type template: str, optional
    :return: str representation of datetime
    :rtype: str
    """
    return datetime_object.strftime(template)
