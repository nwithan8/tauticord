from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import modules.logs as logging
from modules.emojis import EmojiManager
from modules.tautulli.tautulli_connector import (
    TautulliConnector,
)


class Summary(commands.Cog):
    def __init__(self, bot: commands.Bot, tautulli: TautulliConnector, emoji_manager: EmojiManager):
        self.bot = bot
        self._tautulli = tautulli
        self._emoji_manager = emoji_manager
        super().__init__()  # This is required for the cog to work.
        logging.info("Summary cog loaded.")

    @app_commands.command(name="summary", description="Show current activity summary.")
    @app_commands.describe(
        share="Whether to make the response visible to the channel."
    )
    async def movies(self, interaction: discord.Interaction, share: Optional[bool] = False) -> None:
        data_wrapper, count, activity, plex_online = self._tautulli.refresh_data(emoji_manager=self._emoji_manager)
        await interaction.response.send_message(embed=data_wrapper.embed, ephemeral=not share)
