from typing import Union, List

import discord

from modules.discord.models.tautulli_stream_info import TautulliStreamInfo
from modules.emojis import EmojiManager
from modules.tautulli.models.activity import Activity
from modules.text_manager import TextManager


class TautulliActivitySummary:
    def __init__(self,
                 activity: Union[Activity, None],
                 plex_online: bool,
                 server_name: str,
                 emoji_manager: EmojiManager,
                 text_manager: TextManager,
                 streams: List[TautulliStreamInfo] = None,
                 has_plex_pass: bool = False,
                 error_occurred: bool = False,
                 additional_embed_fields: List[dict] = None,
                 additional_embed_footers: List[str] = None):
        self.activity = activity
        self.plex_online = plex_online
        self.has_plex_pass = has_plex_pass
        self.error_occurred = error_occurred
        self.additional_embed_fields = additional_embed_fields or []
        self.additional_embed_footers = additional_embed_footers or []
        self.streams = streams or []
        self._emoji_manager = emoji_manager
        self._server_name = server_name
        self._text_manager = text_manager

    @property
    def embed(self) -> discord.Embed:
        title = f"Current activity on {self._server_name}"
        if len(self.streams) <= 0:
            title = "No current activity"

        embed = discord.Embed(title=title)

        for stream in self.streams:
            embed.add_field(name=stream.get_title(emoji_manager=self._emoji_manager, text_manager=self._text_manager),
                            value=stream.get_body(emoji_manager=self._emoji_manager, text_manager=self._text_manager),
                            inline=False)
        for field in self.additional_embed_fields:
            embed.add_field(name=field['name'], value=field['value'], inline=False)

        footer_text = self._text_manager.overview_footer(no_connection=self.error_occurred,
                                                         activity=self.activity,
                                                         emoji_manager=self._emoji_manager,
                                                         add_termination_tip=self.has_plex_pass)
        if self.additional_embed_footers:
            footer_text += "\n"
        for additional_footer in self.additional_embed_footers:
            footer_text += "\n" + additional_footer

        embed.set_footer(text=footer_text)

        return embed
