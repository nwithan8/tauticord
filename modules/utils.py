import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Any
from urllib.parse import quote_plus


def pretty_print_json(json_data: dict, sort: bool = False) -> str:
    """
    Return a pretty printed JSON m json_data: JSON data to pretty print
    :type json_data: dict
    :param sort: (Optional) sort the keys in the JSON data
    :type sort: bool, optional
    :return: pretty printed JSON string
    :rtype: str
    """
    return json.dumps(json_data, indent=4, sort_keys=sort)


def make_plural(word, count: int, suffix_override: str = 's') -> str:
    if count > 1:
        return f"{word}{suffix_override}"
    return word


def quote(string: str) -> str:
    return f"\"{string}\""


def url_encode(string: str) -> str:
    return quote_plus(string)


def strip_phantom_space(string: str) -> str:
    return string.replace('️', "").replace("\u200b", "").strip()


def is_none_or_empty(value) -> bool:
    return value is None or value == ""


def set_default_if_none_or_empty(value, default) -> Any:
    if is_none_or_empty(value):
        return default
    return value


def seconds_to_minutes(seconds: int) -> int:
    return seconds // 60


def seconds_to_hhmm(seconds: int) -> str:
    """
    Returns a string representation of the given seconds in the format "HH:MM"
    Include hours if 0
    """
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(hours):02d}:{int(minutes):02d}"


def seconds_to_hhmmss(seconds: int) -> str:
    """
    Returns a string representation of the given seconds in the format "HH:MM:SS"
    Include hours if 0
    Include minutes if 0
    """
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def seconds_to_days_hours_minutes_seconds(seconds: int) -> str:
    """
    Returns a string representation of the given seconds in the format "DDd HHh MMm SSs"
    Exclude days if 0
    Exclude hours if 0
    Exclude minutes if 0
    """
    stamp = ""

    days, seconds = divmod(seconds, 86400)
    if days:
        stamp += f"{int(days):02d}d "
    hours, seconds = divmod(seconds, 3600)
    if hours:
        stamp += f"{int(hours):02d}h "
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        stamp += f"{int(minutes):02d}m "
    stamp += f"{int(seconds):02d}s"

    return stamp


def seconds_to_hours_minutes_seconds(seconds: int) -> str:
    """
    Returns a string representation of the given seconds in the format "HHh MMm SSs"
    Exclude hours if 0
    Exclude minutes if 0
    """
    stamp = ""

    hours, seconds = divmod(seconds, 3600)
    if hours:
        stamp += f"{int(hours):02d}h "
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        stamp += f"{int(minutes):02d}m "
    stamp += f"{int(seconds):02d}s"

    return stamp


def seconds_to_hours_minutes(seconds: int) -> str:
    """
    Returns a string representation of the given seconds in the format "HHh MMm"
    Include hours if 0
    """
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(hours):02d}h {int(minutes):02d}m"


def status_code_is_success(status_code: int) -> bool:
    return 200 <= status_code < 300


def extract_boolean(value) -> bool:
    if isinstance(value, bool):
        return value
    if value.lower() in ["true", "t", "yes", "y", "enable", "en", "on", "1"]:
        return True
    elif value.lower() in ["false", "f", "no", "n", "disable", "dis", "off", "0"]:
        return False
    else:
        raise ValueError("Not a boolean: {}".format(value))


def mark_exists(value: Optional[Any]) -> str:
    if value:
        return "Present"
    return "Not Present"


def format_decimal(number: float, denominator: int = 1, decimal_places: int = 1, no_zeros: bool = False) -> str:
    if decimal_places <= 0:
        value = f'{int(number / denominator):d}'
    else:
        value = f'{float(number / denominator):.{decimal_places}f}'

    if no_zeros:
        if value.endswith("."):
            value = value[:-1]
        if value.endswith("." + "0" * decimal_places):
            value = value[:-decimal_places - 1]

    return value


def format_thousands(number: int, delimiter: str = "") -> str:
    if number < 1000:
        return str(number)
    return f"{format_thousands(number // 1000, delimiter)}{delimiter}{number % 1000:03d}"


def _human_size(_bytes, interval: int = 1000, decimal_places: int = 1, no_zeros: bool = False) -> str:
    # Return the given byte size as a human friendly string

    KB = float(interval)
    MB = float(interval ** 2)
    GB = float(interval ** 3)
    TB = float(interval ** 4)

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

    value = format_decimal(number=_bytes, denominator=denominator, decimal_places=decimal_places, no_zeros=no_zeros)
    return f"{value} {letter}"


def human_size(_bytes, decimal_places: int = 1, no_zeros: bool = False) -> str:
    # Return the given byte size as a human friendly string
    value = _human_size(_bytes, interval=1000, decimal_places=decimal_places, no_zeros=no_zeros)
    return f"{value}B"


def human_bitrate(_bytes, decimal_places: int = 1, no_zeros: bool = False) -> str:
    # Return the given bitrate as a human friendly bps, Kbps, Mbps, Gbps, or Tbps string
    value = _human_size(_bytes, interval=1024, decimal_places=decimal_places, no_zeros=no_zeros)
    return f"{value}bps"


def milliseconds_to_minutes_seconds(milliseconds: int) -> str:
    seconds = int(milliseconds / 1000)
    minutes = int(seconds / 60)
    if minutes < 10:
        minutes = f"0{minutes}"
    seconds = int(seconds % 60)
    if seconds < 10:
        seconds = f"0{seconds}"
    return f"{minutes}:{seconds}"


def now() -> datetime:
    return datetime.now()


def now_plus_milliseconds(milliseconds: int) -> datetime:
    return datetime.now() + timedelta(milliseconds=milliseconds)


def limit_text_length(text: str, limit: int, suffix: str = "...") -> str:
    if len(text) <= limit:
        return text

    suffix_length = len(suffix)
    return f"{text[:limit - suffix_length]}{suffix}"


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


def bold(string: str) -> str:
    """
    Return a string wrapped in bold markdown

    :param string: string to wrap in bold markdown
    :type string: str
    :return: string wrapped in bold markdown
    :rtype: str
    """
    return f"**{string}**"


def italic(string: str) -> str:
    """
    Return a string wrapped in italic markdown

    :param string: string to wrap in italic markdown
    :type string: str
    :return: string wrapped in italic markdown
    :rtype: str
    """
    return f"*{string}*"


def underline(string: str) -> str:
    """
    Return a string wrapped in underline markdown

    :param string: string to wrap in underline markdown
    :type string: str
    :return: string wrapped in underline markdown
    :rtype: str
    """
    return f"__{string}__"


def strikethrough(string: str) -> str:
    """
    Return a string wrapped in strikethrough markdown

    :param string: string to wrap in strikethrough markdown
    :type string: str
    :return: string wrapped in strikethrough markdown
    :rtype: str
    """
    return f"~~{string}~~"


def code(string: str) -> str:
    """
    Return a string wrapped in code markdown

    :param string: string to wrap in code markdown
    :type string: str
    :return: string wrapped in code markdown
    :rtype: str
    """
    return f"`{string}`"


def code_block(string: str, language: str = "") -> str:
    """
    Return a string wrapped in code block markdown

    :param string: string to wrap in code block markdown
    :type string: str
    :param language: (Optional) language to use for syntax highlighting
    :type language: str, optional
    :return: string wrapped in code block markdown
    :rtype: str
    """
    return f"```{language}\n{string}```"


def inline_code_block(string: str) -> str:
    """
    Return a string wrapped in inline code block markdown

    :param string: string to wrap in inline code block markdown
    :type string: str
    :return: string wrapped in inline code block markdown
    :rtype: str
    """
    return f"`{string}`"


def block_quote(string: str) -> str:
    """
    Return a string wrapped in block quote markdown

    :param string: string to wrap in block quote markdown
    :type string: str
    :return: string wrapped in block quote markdown
    :rtype: str
    """
    return f"> {string}"


def inline_quote(string: str) -> str:
    """
    Return a string wrapped in inline quote markdown

    :param string: string to wrap in inline quote markdown
    :type string: str
    :return: string wrapped in inline quote markdown
    :rtype: str
    """
    return f">> {string}"


def spoiler(string: str) -> str:
    """
    Return a string wrapped in spoiler markdown

    :param string: string to wrap in spoiler markdown
    :type string: str
    :return: string wrapped in spoiler markdown
    :rtype: str
    """
    return f"||{string}||"


def link(string: str, url: str) -> str:
    """
    Return a string wrapped in link markdown

    :param string: string to wrap in link markdown
    :type string: str
    :param url: url to link to
    :type url: str
    :return: string wrapped in link markdown
    :rtype: str
    """
    return f"[{string}]({url})"


def mention(string: str, user_id: str) -> str:
    """
    Return a string wrapped in mention markdown

    :param string: string to wrap in mention markdown
    :type string: str
    :param user_id: user id to mention
    :type user_id: str
    :return: string wrapped in mention markdown
    :rtype: str
    """
    return f"<@{user_id}>"


def channel_mention(string: str, channel_id: str) -> str:
    """
    Return a string wrapped in channel mention markdown

    :param string: string to wrap in channel mention markdown
    :type string: str
    :param channel_id: channel id to mention
    :type channel_id: str
    :return: string wrapped in channel mention markdown
    :rtype: str
    """
    return f"<#{channel_id}>"


def role_mention(string: str, role_id: str) -> str:
    """
    Return a string wrapped in role mention markdown

    :param string: string to wrap in role mention markdown
    :type string: str
    :param role_id: role id to mention
    :type role_id: str
    :return: string wrapped in role mention markdown
    :rtype: str
    """
    return f"<@&{role_id}>"


def timestamp(ts: int) -> str:
    """
    Return a string wrapped in timestamp markdown

    :param ts: timestamp to wrap in timestamp markdown
    :type ts: int
    :return: string wrapped in timestamp markdown
    :rtype: str
    """
    return f"<t:{ts}>"


def emoji(string: str, emoji_id: str) -> str:
    """
    Return a string wrapped in emoji markdown

    :param string: string to wrap in emoji markdown
    :type string: str
    :param emoji_id: emoji id to use
    :type emoji_id: str
    :return: string wrapped in emoji markdown
    :rtype: str
    """
    return f"<:{string}:{emoji_id}>"


def custom_emoji(string: str, emoji_id: str) -> str:
    """
    Return a string wrapped in custom emoji markdown

    :param string: string to wrap in custom emoji markdown
    :type string: str
    :param emoji_id: emoji id to use
    :type emoji_id: str
    :return: string wrapped in custom emoji markdown
    :rtype: str
    """
    return f"<:{string}:{emoji_id}>"


def custom_emoji_animated(string: str, emoji_id: str) -> str:
    """
    Return a string wrapped in animated custom emoji markdown

    :param string: string to wrap in animated custom emoji markdown
    :type string: str
    :param emoji_id: emoji id to use
    :type emoji_id: str
    :return: string wrapped in animated custom emoji markdown
    :rtype: str
    """
    return f"<a:{string}:{emoji_id}>"


def custom_emoji_url(string: str, emoji_id: str) -> str:
    """
    Return a string wrapped in custom emoji markdown

    :param string: string to wrap in custom emoji markdown
    :type string: str
    :param emoji_id: emoji id to use
    :type emoji_id: str
    :return: string wrapped in custom emoji markdown
    :rtype: str
    """
    return f"[{string}](https://cdn.discordapp.com/emojis/{emoji_id})"


def custom_emoji_animated_url(string: str, emoji_id: str) -> str:
    """
    Return a string wrapped in animated custom emoji markdown

    :param string: string to wrap in animated custom emoji markdown
    :type string: str
    :param emoji_id: emoji id to use
    :type emoji_id: str
    :return: string wrapped in animated custom emoji markdown
    :rtype: str
    """
    return f"[{string}](https://cdn.discordapp.com/emojis/{emoji_id}.gif)"


def custom_emoji_name(string: str, emoji_id: str) -> str:
    """
    Return a string wrapped in custom emoji markdown

    :param string: string to wrap in custom emoji markdown
    :type string: str
    :param emoji_id: emoji id to use
    :type emoji_id: str
    :return: string wrapped in custom emoji markdown
    :rtype: str
    """
    return f":{string}:"


def custom_emoji_animated_name(string: str, emoji_id: str) -> str:
    """
    Return a string wrapped in animated custom emoji markdown

    :param string: string to wrap in animated custom emoji markdown
    :type string: str
    :param emoji_id: emoji id to use
    :type emoji_id: str
    :return: string wrapped in animated custom emoji markdown
    :rtype: str
    """
    return f":{string}:"


def discord_text_channel_name_format(string: str) -> str:
    """
    Return a string formatted as a discord text channel name

    :param string: string to format
    :type string: str
    :return: string formatted as a discord text channel name
    :rtype: str
    """
    # lowercase and replace spaces with dashes
    string = string.lower().replace(" ", "-")
    return string


def get_temporary_file_path(sub_directory: str = None, parent_directory: str = None, file_extension: str = None) -> str:
    """
    Return a temporary file path

    :param sub_directory: (Optional) subdirectory to use
    :type sub_directory: str, optional
    :param parent_directory: (Optional) parent directory to use
    :type parent_directory: str, optional
    :param file_extension: (Optional) file extension to use
    :type file_extension: str, optional
    :return: temporary file path
    :rtype: str
    """
    base = parent_directory or "/tmp"

    if sub_directory:
        base = os.path.join(base, sub_directory)

    os.makedirs(base, exist_ok=True)

    return os.path.join(base, f"{os.urandom(24).hex()}{file_extension or '.tmp'}")


def get_current_directory() -> str:
    return os.getcwd()


def is_docker():
    return os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)


def is_positive_int(n):
    return n.isdigit()


def convert_string_to_bool(bool_string: str) -> bool:
    """
    Careful: True or False is valid. Check if is None to see if this conversion failed
    """
    bool_string = bool_string.strip().lower()
    if bool_string in ['true', 'yes', 'on', 'enable']:
        return True
    elif bool_string in ['false', 'no', 'off', 'disable']:
        return False

    raise ValueError(f"Invalid bool string: {bool_string}")


def convert_bool_to_string(bool_value: bool) -> str:
    if bool_value:
        return "True"
    else:
        return "False"


def convert_bool_to_int(bool_value: bool) -> int:
    if bool_value:
        return 1
    else:
        return 0


def convert_int_to_bool(int_value: int) -> bool:
    if int_value == 1:
        return True
    elif int_value == 0:
        return False

    raise ValueError(f"Invalid int value for bool: {int_value}")


def convert_string_list_to_string(string_list: list[str]) -> str:
    return ",".join(string_list)


def convert_string_to_string_list(string: str) -> list[str]:
    return string.split(",")


def object_to_string_representation(obj: object) -> str:
    """
    Convert an object to a string

    :param obj:
    :return: String representation of the object
    """
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, int):
        return str(obj)
    elif isinstance(obj, float):
        return str(obj)
    elif isinstance(obj, bool):
        return convert_bool_to_string(bool_value=obj)
    elif isinstance(obj, list):
        string_list = [object_to_string_representation(obj=o) for o in obj]
        return convert_string_list_to_string(string_list=string_list)

    raise ValueError(f'Cannot convert type {type(object)} to string representation')


def get_now_timestamp():
    return int(time.time())


def get_days_ago_timestamp(days: int):
    return int(time.mktime((datetime.today() - timedelta(days=days)).timetuple()))


def get_hours_ago_timestamp(hours: int):
    return int(time.mktime((datetime.today() - timedelta(hours=hours)).timetuple()))


def get_minutes_ago_timestamp(minutes: int):
    return int(time.mktime((datetime.today() - timedelta(minutes=minutes)).timetuple()))


def get_seconds_ago_timestamp(seconds: int):
    return int(time.mktime((datetime.today() - timedelta(seconds=seconds)).timetuple()))


def get_days_from_now_timestamp(days: int):
    return int(time.mktime((datetime.today() + timedelta(days=days)).timetuple()))


def get_hours_from_now_timestamp(hours: int):
    return int(time.mktime((datetime.today() + timedelta(hours=hours)).timetuple()))


def get_minutes_from_now_timestamp(minutes: int):
    return int(time.mktime((datetime.today() + timedelta(minutes=minutes)).timetuple()))


def get_seconds_from_now_timestamp(seconds: int):
    return int(time.mktime((datetime.today() + timedelta(seconds=seconds)).timetuple()))


def _bytes_to_hash(_input: bytes) -> str:
    """
    Hash a string with SHA256.
    :param _input: string to hash.
    :return: hashed string.
    """
    return hashlib.sha256(_input).hexdigest()


def _string_to_hash(_input: str) -> str:
    """
    Hash a string with SHA256.
    :param _input: string to hash.
    :return: hashed string.
    """
    return _bytes_to_hash(_input.encode('utf-8'))


def generate_hash(secret: str) -> str:
    """
    Generate a hash from a string.
    :param secret: string to hash.
    :return: hashed string.
    """
    return _string_to_hash(secret)


def hash_matches(_input: str, hashed: str) -> bool:
    """
    Check if a string, when hashed, matches another string.
    :param _input: String to hash and compare to the hashed string.
    :param hashed: Hashed string to compare against.
    :return: True if the string, when hashed, matches the hashed string, False otherwise.
    """
    to_match = _string_to_hash(_input)
    return hmac.compare_digest(to_match, hashed)


def generate_random_alphanumeric_string() -> str:
    """
    Generate a random alphanumeric string.
    :return: random alphanumeric string.
    """
    return secrets.token_urlsafe(24)
