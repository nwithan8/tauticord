from typing import Optional, Callable

import discord
from discord import app_commands
from discord.ext import commands

import modules.logs as logging
from modules.discord import discord_utils
from modules.emojis import EmojiManager
from modules.tautulli.tautulli_connector import (
    TautulliConnector,
)


class Summary(commands.Cog):
    def __init__(self, bot: commands.Bot, tautulli: TautulliConnector, emoji_manager: EmojiManager, admin_check: Callable[[discord.Interaction], bool] = None):
        self.bot = bot
        self._tautulli = tautulli
        self._emoji_manager = emoji_manager
        self._admin_check = admin_check
        super().__init__()  # This is required for the cog to work.
        logging.debug("Summary cog loaded.")

    async def check_admin(self, interaction: discord.Interaction) -> bool:
        if self._admin_check and not self._admin_check(interaction):
            await discord_utils.respond_to_slash_command_with_text(interaction=interaction,
                                                                    text="You do not have permission to use this command.",
                                                                    ephemeral=True)
            return False

        return True

    @app_commands.command(name="summary", description="Show current activity summary.")
    @app_commands.describe(
        share="Whether to make the response visible to the channel."
    )
    async def summary(self, interaction: discord.Interaction, share: Optional[bool] = False) -> None:
        if not await self.check_admin(interaction):
            return

        # Does NOT include new version reminder or stream termination.
        summary = self._tautulli.refresh_data(enable_stream_termination_if_possible=False, emoji_manager=self._emoji_manager)
        await summary.reply_to_slash_command(interaction=interaction, ephemeral=not share)
