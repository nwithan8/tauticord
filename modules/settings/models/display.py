from typing import Optional

from modules.settings.models.anonymity import Anonymity
from modules.settings.models.base import BaseConfig
from modules.settings.models.time import Time


class Display(BaseConfig):
    anonymity: Anonymity
    plex_server_name: str
    thousands_separator: Optional[str] = ""
    time: Time
    use_friendly_names: bool

    def as_dict(self) -> dict:
        return {
            "anonymity": self.anonymity.as_dict(),
            "plex_server_name": self.plex_server_name,
            "thousands_separator": self.thousands_separator,
            "time": self.time.as_dict(),
            "use_friendly_names": self.use_friendly_names
        }
