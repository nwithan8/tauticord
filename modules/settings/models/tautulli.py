from modules.settings.models.base import BaseConfig
from modules.utils import mark_exists


class Tautulli(BaseConfig):
    url: str
    api_key: str
    ignore_ssl: bool
    refresh_interval_seconds: int
    termination_message: str

    def as_dict(self) -> dict:
        return {
            "url": self.url,
            "api_key": mark_exists(self.api_key),
            "ignore_ssl": self.ignore_ssl,
            "refresh_interval_seconds": self.refresh_interval_seconds,
            "termination_message": self.termination_message
        }
