from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import modules.logs as logging
from modules.tautulli_connector import (
    TautulliConnector,
    HomeStatType,
)


def _build_top_media_response_embed(stats: list[dict[str, str]], title: str) -> discord.Embed:
    embed = discord.Embed(title=title, color=0x00ff00)
    for stat in stats:
        embed.add_field(name=stat["title"], value=stat["total_plays"], inline=False)
    return embed


def _build_top_user_response_embed(stats: list[dict[str, str]], title: str) -> discord.Embed:
    embed = discord.Embed(title=title, color=0x00ff00)
    for stat in stats:
        embed.add_field(name=stat["friendly_name"], value=stat["total_plays"], inline=False)
    return embed


class Top(commands.GroupCog, name="top"):
    def __init__(self, bot: commands.Bot, tautulli: TautulliConnector):
        self.bot = bot
        self._tautulli = tautulli
        super().__init__()  # This is required for the cog to work.
        logging.info("Top cog loaded.")

    @app_commands.command(name="movies", description="Show top movies for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        share="Whether to make the response visible to the channel."
    )
    async def movies(self, interaction: discord.Interaction, days: int, share: Optional[bool] = False) -> None:
        limit = 5
        stats = self._tautulli.get_stats_for_x_days(
            stat_type=HomeStatType.TOP_MOVIES, days=days,
            limit=limit)  # TOP_MOVIES is number of plays, POPULAR_MOVIES is number of unique users

        if not stats:
            await interaction.response.send_message("No stats found.", ephemeral=True)
            return

        embed = _build_top_media_response_embed(stats, f"Top movies for past {days} day(s)")
        await interaction.response.send_message(embed=embed, ephemeral=not share)

    @app_commands.command(name="shows", description="Show top shows for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        share="Whether to make the response visible to the channel."
    )
    async def shows(self, interaction: discord.Interaction, days: int, share: Optional[bool] = False) -> None:
        limit = 5
        stats = self._tautulli.get_stats_for_x_days(
            stat_type=HomeStatType.TOP_TV, days=days,
            limit=limit)  # TOP_TV is number of plays, POPULAR_TV is number of unique users

        if not stats:
            await interaction.response.send_message("No stats found.", ephemeral=True)
            return

        embed = _build_top_media_response_embed(stats, f"Top shows for past {days} day(s)")
        await interaction.response.send_message(embed=embed, ephemeral=not share)

    @app_commands.command(name="users", description="Show top users for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        share="Whether to make the response visible to the channel."
    )
    async def users(self, interaction: discord.Interaction, days: int, share: Optional[bool] = False) -> None:
        limit = 5
        stats = self._tautulli.get_stats_for_x_days(
            stat_type=HomeStatType.TOP_USERS, days=days, limit=limit
        )

        if not stats:
            await interaction.response.send_message("No stats found.", ephemeral=True)
            return

        embed = _build_top_user_response_embed(stats, f"Top users for past {days} day(s)")
        await interaction.response.send_message(embed=embed, ephemeral=not share)
