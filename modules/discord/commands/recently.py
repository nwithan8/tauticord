from typing import Optional, Callable

import discord
from discord import app_commands
from discord.ext import commands

import modules.logs as logging
from modules.discord import discord_utils
from modules.discord.models.tautulli_recently_added_summary import TautulliRecentlyAddedSummary
from modules.tautulli.tautulli_connector import (
    TautulliConnector,
)


class Recently(commands.GroupCog, name="recently"):
    def __init__(self, bot: commands.Bot, tautulli: TautulliConnector,
                 admin_check: Callable[[discord.Interaction], bool] = None):
        self.bot = bot
        self._tautulli = tautulli
        self._admin_check = admin_check
        super().__init__()  # This is required for the cog to work.
        logging.debug("Recently cog loaded.")

    @app_commands.command(name="added", description="Show recently added media.")
    @app_commands.describe(
        media_type="The type of media to filter by.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.rename(media_type="media-type")
    @app_commands.choices(
        media_type=[
            discord.app_commands.Choice(name="Movies", value="movie"),
            discord.app_commands.Choice(name="Shows", value="show"),
        ]
    )
    async def added(self,
                    interaction: discord.Interaction,
                    media_type: Optional[discord.app_commands.Choice[str]] = None,
                    share: Optional[bool] = False) -> None:
        # This command is public, no admin restrictions

        # Defer the response to give more than the default 3 seconds to respond.
        await discord_utils.respond_to_slash_command_with_thinking(interaction=interaction, ephemeral=not share)

        limit = 5
        if media_type:
            media_type = media_type.value

        summary: TautulliRecentlyAddedSummary = self._tautulli.get_recently_added_media_summary(count=limit,
                                                                                                media_type=media_type)
        await summary.reply_to_slash_command(interaction=interaction, ephemeral=not share)
