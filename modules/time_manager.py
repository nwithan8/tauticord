from datetime import datetime

import discord.utils
from pydantic import BaseModel

from modules import utils


class TimeManager(BaseModel):
    def now(self) -> datetime:
        return discord.utils.utcnow()

    def now_unix_timestamp(self) -> str:
        _timestamp = int(self.now().timestamp())
        return utils.timestamp(ts=_timestamp)

    def now_plus_milliseconds(self, milliseconds: int) -> datetime:
        return utils.now_plus_milliseconds(milliseconds)

    def now_plus_milliseconds_unix_timestamp(self, milliseconds: int) -> str:
        _timestamp = int(self.now_plus_milliseconds(milliseconds).timestamp())
        return utils.timestamp(ts=_timestamp)
