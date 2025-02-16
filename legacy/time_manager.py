from datetime import datetime

from modules import utils


class TimeManager:
    def __init__(self, timezone: str, military_time: bool) -> None:
        self._timezone: str = timezone
        self._military_time: bool = military_time

    def now(self) -> datetime:
        return utils.now()

    def now_string(self) -> str:
        _datetime = self.now()
        return utils.datetime_to_string(datetime_object=_datetime, template=("%H:%M" if self._military_time else "%I:%M %p"))

    def now_plus_milliseconds(self, milliseconds: int) -> datetime:
        return utils.now_plus_milliseconds(milliseconds)

    def now_plus_milliseconds_string(self, milliseconds: int) -> str:
        _datetime = self.now_plus_milliseconds(milliseconds)
        return utils.datetime_to_string(datetime_object=_datetime, template=("%H:%M" if self._military_time else "%I:%M %p"))

    def __repr__(self):
        return f"TimeManager(timezone={self._timezone}, military_time={self._military_time})"

    def __str__(self):
        return f"TimeManager(timezone={self._timezone}, military_time={self._military_time})"
