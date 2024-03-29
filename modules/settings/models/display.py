from typing import Optional

from modules.settings.models.anonymity import Anonymity
from modules.settings.models.base import BaseConfig
from modules.settings.models.time import Time
from modules.text_manager import TextManager


class Display(BaseConfig):
    anonymity: Anonymity
    plex_server_name: str
    thousands_separator: Optional[str] = ""
    time: Time
    use_friendly_names: bool

    @property
    def text_manager(self) -> TextManager:
        return TextManager(
            hide_usernames=self.anonymity.hide_usernames,
            hide_player_names=self.anonymity.hide_player_names,
            hide_platforms=self.anonymity.hide_platforms,
            hide_quality=self.anonymity.hide_quality,
            hide_bandwidth=self.anonymity.hide_bandwidth,
            hide_transcoding=self.anonymity.hide_transcode_decision,
            hide_progress=self.anonymity.hide_progress,
            hide_eta=self.anonymity.hide_eta,
            use_friendly_names=self.use_friendly_names,
            time_manager=self.time.time_manager
        )

    def as_dict(self) -> dict:
        return {
            "anonymity": self.anonymity.as_dict(),
            "plex_server_name": self.plex_server_name,
            "thousands_separator": self.thousands_separator,
            "time": self.time.as_dict(),
            "use_friendly_names": self.use_friendly_names
        }
