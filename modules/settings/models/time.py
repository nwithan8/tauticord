from modules.settings.models.base import BaseConfig

from modules.time_manager import TimeManager


class Time(BaseConfig):
    tautulli_server_time_zone: str
    use_24_hour_time: bool

    @property
    def time_manager(self):
        return TimeManager(
            timezone=self.tautulli_server_time_zone,
            use_24_hour_time=self.use_24_hour_time)

    def as_dict(self) -> dict:
        return {
            "tautulli_server_time_zone": self.tautulli_server_time_zone,
            "use_24_hour_time": self.use_24_hour_time
        }
