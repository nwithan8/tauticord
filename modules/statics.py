# Number 1-9, and A-Z
emojis = [
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "🇦",
    "🇧",
    "🇨",
    "🇩",
    "🇪",
    "🇫",
    "🇬",
    "🇭",
    "🇮",
    "🇯",
    "🇰",
    "🇱",
    "🇲",
    "🇳",
    "🇴",
    "🇵",
    "🇶",
    "🇷",
    "🇸",
    "🇹",
    "🇺",
    "🇻",
    "🇼",
    "🇽",
    "🇾",
    "🇿",
]


def emoji_from_stream_number(number):
    return emojis[number - 1]


def stream_number_from_emoji(emoji):
    return emojis.index(str(emoji)) + 1


switcher = {
    "playing": "▶️",
    "paused": "⏸",
    "stopped": "⏹",
    "buffering": "⏳",
    "error": "⚠️"
}

media_type_icons = {'episode': '📺', 'track': '🎧', 'movie': '🎞', 'clip': '🎬', 'photo': '🖼', 'live': '📡'}

sessions_message = """{stream_count} {word}"""
transcodes_message = """{transcode_count} {word}"""
bandwidth_message = """🌐 {bandwidth}"""
lan_bandwidth_message = """(🏠 {bandwidth})"""

session_title_message = """{emoji} | {icon} {media_type_icon} {username}: *{title}*"""
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
