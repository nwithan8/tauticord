from datetime import datetime, timedelta

from pytz import timezone


def make_plural(word, count: int, suffix_override: str = 's') -> str:
    if count > 1:
        return f"{word}{suffix_override}"
    return word

def quote(string: str) -> str:
    return f"\"{string}\""

def status_code_is_success(status_code: int) -> bool:
    return 200 <= status_code < 300

def format_fraction(number: float, denominator: int = 1, decimal_places: int = 1) -> str:
    if decimal_places <= 0:
        return f'{int(number / denominator):d}'
    else:
        return f'{float(number / denominator):.{decimal_places}f}'

def format_thousands(number: int, delimiter: str = "") -> str:
    if number < 1000:
        return str(number)
    return f"{format_thousands(number // 1000, delimiter)}{delimiter}{number % 1000:03d}"

def human_bitrate(_bytes, decimal_places: int = 1) -> str:
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

    value = format_fraction(number=_bytes, denominator=denominator, decimal_places=decimal_places)
    return f"{value} {letter}bps"


def milliseconds_to_minutes_seconds(milliseconds: int) -> str:
    seconds = int(milliseconds / 1000)
    minutes = int(seconds / 60)
    if minutes < 10:
        minutes = f"0{minutes}"
    seconds = int(seconds % 60)
    if seconds < 10:
        seconds = f"0{seconds}"
    return f"{minutes}:{seconds}"

def now(timezone_code: str = None) -> datetime:
    if timezone_code:
        return datetime.now(timezone(timezone_code))  # will raise exception if invalid timezone_code
    return datetime.now()

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
