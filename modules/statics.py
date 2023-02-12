# Number 1-9, and A-Z
from typing import Optional

EMOJIS_FOLDER = "resources/emojis"

sessions_message = """{stream_count} {word}"""
transcodes_message = """{transcode_count} {word}"""
bandwidth_message = """{emoji} {bandwidth}"""
lan_bandwidth_message = """({emoji} {bandwidth})"""

session_title_message = """{emoji} | {icon} {media_type_icon} {username}: *{title}*"""
session_user_message = """{emoji} **{username}**"""
session_player_message = """__Player__: {product} ({player})"""
session_details_message = """__Quality__: {quality_profile} ({bandwidth}){transcoding}"""
session_progress_message = """__Progress__: {progress} (ETA: {eta})"""

voice_channel_order = {
    'count': 1,
    'transcodes': 2,
    'bandwidth': 3,
    'localBandwidth': 4,
    'remoteBandwidth': 5
}


KEY_STATS_CATEGORY_NAME = "stats_category_name"
KEY_COUNT = "count"
KEY_TRANSCODE_COUNT = "transcode_count"
KEY_BANDWIDTH = "bandwidth"
KEY_LAN_BANDWIDTH = "lan_bandwidth"
KEY_REMOTE_BANDWIDTH = "remote_bandwidth"
KEY_STATS = "stats"
KEY_PLEX_STATUS = "plex_status"
KEY_REFRESH_TIME = "refresh_time"
KEY_LIBRARIES_CATEGORY_NAME = "libraries_category_name"
KEY_LIBRARIES = "libraries"
