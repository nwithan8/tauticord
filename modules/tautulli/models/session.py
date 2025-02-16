import modules.logs as logging
from modules import utils
from modules.emojis import EmojiManager
from modules.time_manager import TimeManager


class Session:
    def __init__(self, session_data, time_manager: TimeManager):
        self._data = session_data
        self._time_manager = time_manager

    @property
    def duration_milliseconds(self) -> int:
        value = self._data.get('duration', 0)
        try:
            value = int(value)
        except:
            value = 0
        return int(value)

    @property
    def location_milliseconds(self) -> int:
        value = self._data.get('view_offset', 0)
        try:
            value = int(value)
        except:
            value = 0
        return int(value)

    @property
    def progress_percentage(self) -> int:
        if not self.duration_milliseconds:
            return 0
        return int(self.location_milliseconds / self.duration_milliseconds)

    @property
    def progress_marker(self) -> str:
        current_progress_min_sec = utils.milliseconds_to_minutes_seconds(milliseconds=self.location_milliseconds)
        total_min_sec = utils.milliseconds_to_minutes_seconds(milliseconds=self.duration_milliseconds)
        return f"{current_progress_min_sec}/{total_min_sec}"

    @property
    def eta(self) -> str:
        if not self.duration_milliseconds or not self.location_milliseconds:
            return "Unknown"
        milliseconds_remaining = self.duration_milliseconds - self.location_milliseconds
        return self._time_manager.now_plus_milliseconds_unix_timestamp(milliseconds=milliseconds_remaining)

    @property
    def title(self) -> str:
        if self._data.get('live'):
            return f"{self._data.get('grandparent_title', '')} - {self._data['title']}"
        elif self._data['media_type'] == 'episode':
            return f"{self._data.get('grandparent_title', '')} - S{self._data.get('parent_title', '').replace('Season ', '').zfill(2)}E{self._data.get('media_index', '').zfill(2)} - {self._data['title']}"
        else:
            return self._data.get('full_title')

    def get_status_icon(self, emoji_manager: EmojiManager) -> str:
        """
        Get icon for a stream state
        :return: emoji icon
        """
        return emoji_manager.get_emoji(key=self._data.get('state', ""))

    def get_type_icon(self, emoji_manager: EmojiManager) -> str:
        key = self._data.get('media_type', "")
        if self._data.get('live'):
            key = 'live'
        emoji = emoji_manager.get_emoji(key=key)
        if not emoji:
            logging.debug(
                "New media_type to pick icon for: {}: {}".format(self._data['title'], self._data['media_type']))
            return '🎁'
        return emoji

    @property
    def id(self) -> str:
        return self._data['session_id']

    @property
    def username(self) -> str:
        return self._data['username']

    @property
    def friendly_name(self) -> str:
        return self._data['friendly_name']

    @property
    def product(self) -> str:
        return self._data['product']

    @property
    def player(self) -> str:
        return self._data['player']

    @property
    def quality_profile(self) -> str:
        return self._data['quality_profile']

    @property
    def bandwidth(self) -> str:
        value = self._data.get('bandwidth', 0)
        try:
            value = int(value)
        except:
            value = 0
        return utils.human_bitrate(float(value) * 1024)

    @property
    def is_transcoding(self) -> bool:
        return self.stream_container_decision == 'transcode'

    @property
    def transcoding_stub(self) -> str:
        return ' (Transcode)' if self.is_transcoding else ''

    @property
    def stream_container_decision(self) -> str:
        return self._data['stream_container_decision']
