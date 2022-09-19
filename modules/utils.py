from datetime import datetime, timedelta

from pytz import timezone


def make_plural(word, count: int, suffix_override: str = 's') -> str:
    if count > 1:
        return f"{word}{suffix_override}"
    return word


def _human_bitrate(number, denominator: int = 1, letter: str = "", d: int = 1) -> str:
    if d <= 0:
        return f'{int(number / denominator):d} {letter}bps'
    else:
        return f'{float(number / denominator):.{d}f} {letter}bps'


def human_bitrate(_bytes, d: int = 1) -> str:
    # Return the given bitrate as a human friendly bps, Kbps, Mbps, Gbps, or Tbps string

    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    denominator = 1
    letter = ""
    if _bytes < KB:
        pass
    elif KB <= _bytes < MB:
        denominator = KB
        letter = "k"
    elif MB <= _bytes < GB:
        denominator = MB
        letter = "M"
    elif GB <= _bytes < TB:
        denominator = GB
        letter = "G"
    else:
        denominator = TB
        letter = "T"

    return _human_bitrate(_bytes, denominator=denominator, letter=letter, d=d)


def milliseconds_to_minutes_seconds(milliseconds: int) -> str:
    seconds = int(milliseconds / 1000)
    minutes = int(seconds / 60)
    if minutes < 10:
        minutes = f"0{minutes}"
    seconds = int(seconds % 60)
    if seconds < 10:
        seconds = f"0{seconds}"
    return f"{minutes}:{seconds}"


def now_plus_milliseconds(milliseconds: int, timezone_code: str = None) -> datetime:
    if timezone_code:
        now = datetime.now(timezone(timezone_code))  # will raise exception if invalid timezone_code
    else:
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
