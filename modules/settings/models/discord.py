from typing import Optional

from modules.settings.models.base import BaseConfig
from modules.utils import mark_exists


class StatusMessage(BaseConfig):
    enable: bool
    activity_name: Optional[str]
    custom_message: Optional[str]
    show_stream_count: bool

    @property
    def should_update_on_startup(self) -> bool:
        return self.enable

    @property
    def should_update_with_activity(self) -> bool:
        return self.enable

    def message(self, stream_count: int, fallback: Optional[str] = None) -> str:
        if self.custom_message:
            return self.custom_message

        if fallback:
            return fallback

        if self.show_stream_count:
            return f"Currently {stream_count} stream{'s' if stream_count != 1 else ''} active"
        else:
            return "https://github.com/nwithan8/tauticord"

    def as_dict(self) -> dict:
        return {
            "enable": self.enable,
            "activity_name": self.activity_name,
            "custom_message": self.custom_message,
            "show_stream_count": self.show_stream_count
        }


class Discord(BaseConfig):
    admin_ids: list[int]
    bot_token: str
    channel_name: str
    enable_slash_commands: bool
    use_summary_message: bool
    enable_termination: bool
    server_id: int
    status_message_settings: StatusMessage

    def as_dict(self) -> dict:
        return {
            "admin_ids": self.admin_ids,
            "bot_token": mark_exists(self.bot_token),
            "channel_name": self.channel_name,
            "enable_slash_commands": self.enable_slash_commands,
            "use_summary_message": self.use_summary_message,
            "enable_termination": self.enable_termination,
            "server_id": self.server_id,
            "status_message_settings": self.status_message_settings.as_dict()
        }
