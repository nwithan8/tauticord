from modules.settings.models.base import BaseConfig
from modules.utils import mark_exists


class Discord(BaseConfig):
    admin_ids: list[int]
    bot_token: str
    channel_name: str
    enable_slash_commands: bool
    has_discord_nitro: bool
    use_summary_message: bool
    server_id: int

    def as_dict(self) -> dict:
        return {
            "admin_ids": self.admin_ids,
            "bot_token": mark_exists(self.bot_token),
            "channel_name": self.channel_name,
            "enable_slash_commands": self.enable_slash_commands,
            "has_discord_nitro": self.has_discord_nitro,
            "use_summary_message": self.use_summary_message,
            "server_id": self.server_id
        }
