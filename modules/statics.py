# Number 1-9, and A-Z
from typing import Optional

EMOJIS_FOLDER = "resources/emojis"

sessions_message = """{stream_count} {word}"""
transcodes_message = """{transcode_count} {word}"""
bandwidth_message = """{emoji} {bandwidth}"""
lan_bandwidth_message = """({emoji} {bandwidth})"""

session_title_message = """{emoji} | {icon} {media_type_icon} *{title}*"""
session_user_message = """{emoji} **{username}**"""
session_player_message = """{emoji} **{product}** ({player})"""
session_details_message = """{emoji} **{quality_profile}** ({bandwidth}){transcoding}"""
session_progress_message = """{emoji} **{progress}** (ETA: {eta})"""

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
KEY_SHOW_TV_EPISODES = "show_tv_episodes"
KEY_SHOW_TV_SERIES = "show_tv_series"
KEY_SHOW_MUSIC_ARTISTS = "show_music_artists"
KEY_SHOW_MUSIC_TRACKS = "show_music_tracks"
