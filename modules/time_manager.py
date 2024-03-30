from datetime import datetime

from pydantic import BaseModel

from modules import utils


class TimeManager(BaseModel):
    timezone: str
    use_24_hour_time: bool

    @property
    def time_format(self) -> str:
        return "%H:%M" if self.use_24_hour_time else "%I:%M %p"

    def now(self) -> datetime:
        return utils.now(self.timezone)

    def now_string(self) -> str:
        _datetime = self.now()
        return utils.datetime_to_string(datetime_object=_datetime,
                                        template=self.time_format)

    def now_plus_milliseconds(self, milliseconds: int) -> datetime:
        return utils.now_plus_milliseconds(milliseconds, self.timezone)

    def now_plus_milliseconds_string(self, milliseconds: int) -> str:
        _datetime = self.now_plus_milliseconds(milliseconds)
        return utils.datetime_to_string(datetime_object=_datetime,
                                        template=self.time_format)
