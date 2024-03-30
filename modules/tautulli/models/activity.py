from typing import Union, List

from modules import utils
from modules.emojis import EmojiManager
from modules.tautulli.models.session import Session
from modules.time_manager import TimeManager


class Activity:
    def __init__(self, activity_data, time_manager: TimeManager, emoji_manager: EmojiManager):
        self._data = activity_data
        self._time_manager = time_manager
        self._emoji_manager = emoji_manager

    @property
    def stream_count(self) -> int:
        value = self._data.get('stream_count', 0)
        try:
            return int(value)
        except:
            return 0

    @property
    def transcode_count(self) -> int:
        # TODO: Tautulli is reporting the wrong data:
        # https://github.com/Tautulli/Tautulli/blob/444b138e97a272e110fcb4364e8864348eee71c3/plexpy/webserve.py#L6000
        # Judgment there made by transcode_decision
        # We want to consider stream_container_decision
        return max([0, [s.is_transcoding for s in self.sessions].count(True)])

    @property
    def total_bandwidth(self) -> Union[str, None]:
        value = self._data.get('total_bandwidth', 0)
        try:
            return utils.human_bitrate(float(value) * 1024)
        except:
            return None

    @property
    def lan_bandwidth(self) -> Union[str, None]:
        value = self._data.get('lan_bandwidth', 0)
        try:
            return utils.human_bitrate(float(value) * 1024)
        except:
            return None

    @property
    def wan_bandwidth(self) -> Union[str, None]:
        total = self._data.get('total_bandwidth', 0)
        lan = self._data.get('lan_bandwidth', 0)
        value = total - lan
        try:
            return utils.human_bitrate(float(value) * 1024)
        except:
            return None

    @property
    def sessions(self) -> List[Session]:
        return [Session(session_data=session_data, time_manager=self._time_manager) for session_data in
                self._data.get('sessions', [])]
