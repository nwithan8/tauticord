from modules.settings.models.base import BaseConfig

from modules.time_manager import TimeManager


class Time(BaseConfig):
    @property
    def time_manager(self):
        return TimeManager()

    def as_dict(self) -> dict:
        return {
        }
