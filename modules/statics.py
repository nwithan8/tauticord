# Number 1-9, and A-Z
import subprocess
import sys

VERSION = "VERSIONADDEDBYGITHUB"
COPYRIGHT = "Copyright © YEARADDEDBYGITHUB Nate Harris. All rights reserved."
UNKNOWN_COMMIT_HASH = "unknown-commit"

STANDARD_EMOJIS_FOLDER = "resources/emojis/standard"
NITRO_EMOJIS_FOLDER = "resources/emojis/nitro"

MONITORED_DISK_SPACE_FOLDER = "/monitor"

BOT_PREFIX = "tc-"

VOICE_CHANNEL_ORDER = {
    'count': 1,
    'transcodes': 2,
    'bandwidth': 3,
    'localBandwidth': 4,
    'remoteBandwidth': 5
}

MAX_EMBED_FIELD_NAME_LENGTH = 200  # 256 - estimated emojis + flairs + safety margin

KEY_STATS_CATEGORY_NAME = "stats_category_name"
KEY_COUNT = "count"
KEY_TRANSCODE_COUNT = "transcode_count"
KEY_BANDWIDTH = "bandwidth"
KEY_LAN_BANDWIDTH = "lan_bandwidth"
KEY_REMOTE_BANDWIDTH = "remote_bandwidth"
KEY_STATS = "stats"
KEY_PLEX_STATUS = "plex_status"
KEY_PLEX_STATUS_USE_EMOJI = "plex_status_emoji"
KEY_REFRESH_TIME = "refresh_time"
KEY_LIBRARIES_CATEGORY_NAME = "libraries_category_name"
KEY_LIBRARIES = "libraries"
KEY_COMBINED_LIBRARIES = "combined_libraries"
KEY_USE_EMOJIS = "use_emojis"
KEY_SHOW_TV_EPISODES = "show_tv_episodes"
KEY_SHOW_TV_SERIES = "show_tv_series"
KEY_SHOW_MUSIC_ARTISTS = "show_music_artists"
KEY_SHOW_MUSIC_TRACKS = "show_music_tracks"
KEY_STATS_CHANNEL_IDS = "stat_channel_ids"
KEY_USE_STATS_CHANNEL_IDS = "use_stat_channel_ids"
KEY_STREAM_COUNT_CHANNEL_ID = "stream_count_channel_id"
KEY_TRANSCODE_COUNT_CHANNEL_ID = "transcode_count_channel_id"
KEY_BANDWIDTH_CHANNEL_ID = "bandwidth_channel_id"
KEY_LAN_BANDWIDTH_CHANNEL_ID = "lan_bandwidth_channel_id"
KEY_REMOTE_BANDWIDTH_CHANNEL_ID = "remote_bandwidth_channel_id"
KEY_PLEX_STATUS_CHANNEL_ID = "plex_status_channel_id"
KEY_STATUS = "status"

KEY_TIME_MANAGER = "time_settings"

KEY_HIDE_USERNAMES = "hide_usernames"
KEY_HIDE_PLATFORMS = "hide_platforms"
KEY_HIDE_PLAYER_NAMES = "anonymize_players"
KEY_HIDE_QUALITY = "hide_quality"
KEY_HIDE_BANDWIDTH = "hide_bandwidth"
KEY_HIDE_TRANSCODING = "hide_transcoding"
KEY_HIDE_PROGRESS = "hide_progress"
KEY_HIDE_ETA = "hide_eta"
KEY_USE_FRIENDLY_NAMES = "use_friendly_names"

KEY_PERFORMANCE_CATEGORY_NAME = "performance_category_name"
KEY_PERFORMANCE_MONITOR_TAUTULLI_USER_COUNT = "performance_monitor_tautulli_user_count"
KEY_PERFORMANCE_MONITOR_DISK_SPACE = "performance_monitor_disk_space"
KEY_PERFORMANCE_MONITOR_DISK_SPACE_PATH = "performance_monitor_disk_space_path"
KEY_PERFORMANCE_MONITOR_CPU = "performance_monitor_cpu"
KEY_PERFORMANCE_MONITOR_MEMORY = "performance_monitor_memory"

MAX_STREAM_COUNT = 36

ENCODING_SEPARATOR_1 = "%"
ENCODING_SEPARATOR_2 = "#"
ENCODING_SEPARATOR_3 = "@"

ASCII_ART = """___________________  ______________________________________________ 
___  __/__    |_  / / /__  __/___  _/_  ____/_  __ \__  __ \__  __ \\
__  /  __  /| |  / / /__  /   __  / _  /    _  / / /_  /_/ /_  / / /
_  /   _  ___ / /_/ / _  /   __/ /  / /___  / /_/ /_  _, _/_  /_/ / 
/_/    /_/  |_\____/  /_/    /___/  \____/  \____/ /_/ |_| /_____/  
"""

INFO_SUMMARY = f"""Version: {VERSION}
"""


def get_sha_hash(sha: str) -> str:
    return f"git-{sha[0:7]}"


def get_last_commit_hash() -> str:
    """
    Get the seven character commit hash of the last commit.
    """
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except subprocess.SubprocessError:
        sha = UNKNOWN_COMMIT_HASH

    return get_sha_hash(sha)


def is_git() -> bool:
    return "GITHUB" in VERSION


def get_version() -> str:
    if not is_git():
        return VERSION

    return get_last_commit_hash()


def splash_logo() -> str:
    version = get_version()
    return f"""
{ASCII_ART}
Version {version}, Python {sys.version}

{COPYRIGHT}
"""
