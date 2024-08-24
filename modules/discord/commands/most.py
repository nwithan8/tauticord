from typing import Optional, Callable

import discord
from discord import app_commands
from discord.ext import commands

import modules.logs as logging
from modules.discord.views import EmbedColor
from modules.tautulli.tautulli_connector import (
    TautulliConnector,
    HomeStatType,
    StatMetricType,
)
from modules.utils import minutes_to_hhmm


def _build_response_embed(stats: list[dict[str, str]], title: str, name_key: str,
                          convert_time: bool = False) -> discord.Embed:
    embed = discord.Embed(title=title, color=EmbedColor.DARK_ORANGE.value)
    for stat in stats:
        value = stat['total']
        if convert_time:
            value = minutes_to_hhmm(int(value))
        embed.add_field(name=stat[name_key], value=value, inline=False)
    return embed


class Most(commands.GroupCog, name="most"):
    def __init__(self, bot: commands.Bot, tautulli: TautulliConnector,
                 admin_check: Callable[[discord.Interaction], bool] = None):
        self.bot = bot
        self._tautulli = tautulli
        self._admin_check = admin_check
        super().__init__()  # This is required for the cog to work.
        logging.debug("Most cog loaded.")

    async def check_admin(self, interaction: discord.Interaction) -> bool:
        if self._admin_check and not self._admin_check(interaction):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return False

        return True

    async def _build_and_send_response(self,
                                       interaction: discord.Interaction,
                                       stat_type: HomeStatType,
                                       metric: str,
                                       days: int,
                                       name_key: str,
                                       share: Optional[bool] = False) -> None:
        passed_admin_check = await self.check_admin(interaction)
        if not passed_admin_check:
            return

        limit = 5
        stats = self._tautulli.get_stats_for_x_days(stat_type=stat_type, metric=metric, days=days, limit=limit)

        if not stats:
            await interaction.response.send_message("No stats found.", ephemeral=True)
            return

        # Switch case setting the title_prefix based on the stat_type
        title_prefix = ""
        match stat_type:
            case HomeStatType.TOP_MOVIES:
                title_prefix = "watched movies"
            case HomeStatType.POPULAR_MOVIES:
                title_prefix = "popular movies"
            case HomeStatType.TOP_TV:
                title_prefix = "watched shows"
            case HomeStatType.POPULAR_TV:
                title_prefix = "popular shows"
            case HomeStatType.TOP_MUSIC:
                title_prefix = "played artists"
            case HomeStatType.POPULAR_MUSIC:
                title_prefix = "popular artists"
            case HomeStatType.TOP_LIBRARIES:
                title_prefix = "active libraries"
            case HomeStatType.TOP_USERS:
                title_prefix = "active users"
            case HomeStatType.TOP_PLATFORMS:
                title_prefix = "active platforms"

        embed = _build_response_embed(stats=stats,
                                      title=f"Most {title_prefix} for past {days} day(s), by {metric}",
                                      name_key=name_key,
                                      convert_time=metric == StatMetricType.DURATION.value)
        await interaction.response.send_message(embed=embed, ephemeral=not share)

    @app_commands.command(name="watched-movies", description="Show most watched movies for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        metric="The metric by which to calculate the stats. Default is plays.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="plays", value=StatMetricType.PLAYS.value),
        app_commands.Choice(name="duration", value=StatMetricType.DURATION.value)
    ])
    async def watched_movies(self,
                             interaction: discord.Interaction,
                             days: int,
                             metric: discord.app_commands.Choice[str],
                             share: Optional[bool] = False) -> None:
        await self._build_and_send_response(
            interaction=interaction,
            stat_type=HomeStatType.TOP_MOVIES,
            metric=metric.value,
            days=days,
            name_key="title",
            share=share
        )

    @app_commands.command(name="popular-movies", description="Show popular movies for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        metric="The metric by which to calculate the stats. Default is plays.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="plays", value=StatMetricType.PLAYS.value),
        app_commands.Choice(name="duration", value=StatMetricType.DURATION.value)
    ])
    async def popular_movies(self,
                             interaction: discord.Interaction,
                             days: int,
                             metric: discord.app_commands.Choice[str],
                             share: Optional[bool] = False) -> None:

        await self._build_and_send_response(
            interaction=interaction,
            stat_type=HomeStatType.POPULAR_MOVIES,
            days=days,
            metric=metric.value,
            name_key="title",
            share=share
        )

    @app_commands.command(name="watched-shows", description="Show top shows for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        metric="The metric by which to calculate the stats. Default is plays.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="plays", value=StatMetricType.PLAYS.value),
        app_commands.Choice(name="duration", value=StatMetricType.DURATION.value)
    ])
    async def watched_shows(self,
                            interaction: discord.Interaction,
                            days: int,
                            metric: discord.app_commands.Choice[str],
                            share: Optional[bool] = False) -> None:
        await self._build_and_send_response(
            interaction=interaction,
            stat_type=HomeStatType.TOP_TV,
            metric=metric.value,
            days=days,
            name_key="title",
            share=share
        )

    @app_commands.command(name="popular-shows", description="Show popular shows for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        metric="The metric by which to calculate the stats. Default is plays.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="plays", value=StatMetricType.PLAYS.value),
        app_commands.Choice(name="duration", value=StatMetricType.DURATION.value)
    ])
    async def popular_shows(self,
                            interaction: discord.Interaction,
                            days: int,
                            metric: discord.app_commands.Choice[str],
                            share: Optional[bool] = False) -> None:
        await self._build_and_send_response(
            interaction=interaction,
            stat_type=HomeStatType.POPULAR_TV,
            days=days,
            metric=metric.value,
            name_key="title",
            share=share
        )

    @app_commands.command(name="played-artists", description="Show top artists for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="plays", value=StatMetricType.PLAYS.value),
        app_commands.Choice(name="duration", value=StatMetricType.DURATION.value)
    ])
    async def played_artists(self,
                             interaction: discord.Interaction,
                             days: int,
                             metric: discord.app_commands.Choice[str],
                             share: Optional[bool] = False) -> None:
        await self._build_and_send_response(
            interaction=interaction,
            stat_type=HomeStatType.TOP_MUSIC,
            metric=metric.value,
            days=days,
            name_key="title",
            share=share
        )

    @app_commands.command(name="popular-artists", description="Show popular artists for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        metric="The metric by which to calculate the stats. Default is plays.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="plays", value=StatMetricType.PLAYS.value),
        app_commands.Choice(name="duration", value=StatMetricType.DURATION.value)
    ])
    async def popular_artists(self,
                              interaction: discord.Interaction,
                              days: int,
                              metric: discord.app_commands.Choice[str],
                              share: Optional[bool] = False) -> None:
        await self._build_and_send_response(
            interaction=interaction,
            stat_type=HomeStatType.POPULAR_MUSIC,
            metric=metric.value,
            days=days,
            name_key="title",
            share=share
        )

    @app_commands.command(name="active-libraries", description="Show active libraries for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        metric="The metric by which to calculate the stats. Default is plays.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="plays", value=StatMetricType.PLAYS.value),
        app_commands.Choice(name="duration", value=StatMetricType.DURATION.value)
    ])
    async def active_libraries(self,
                               interaction: discord.Interaction,
                               days: int,
                               metric: discord.app_commands.Choice[str],
                               share: Optional[bool] = False) -> None:
        await self._build_and_send_response(
            interaction=interaction,
            stat_type=HomeStatType.TOP_LIBRARIES,
            metric=metric.value,
            days=days,
            name_key="section_name",
            share=share
        )

    @app_commands.command(name="active-users", description="Show active users for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        metric="The metric by which to calculate the stats. Default is plays.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="plays", value=StatMetricType.PLAYS.value),
        app_commands.Choice(name="duration", value=StatMetricType.DURATION.value)
    ])
    async def active_users(self,
                           interaction: discord.Interaction,
                           days: int,
                           metric: discord.app_commands.Choice[str],
                           share: Optional[bool] = False) -> None:
        await self._build_and_send_response(
            interaction=interaction,
            stat_type=HomeStatType.TOP_USERS,
            metric=metric.value,
            days=days,
            name_key="friendly_name",
            share=share
        )

    @app_commands.command(name="active-platforms", description="Show active platforms for a number of days.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        metric="The metric by which to calculate the stats. Default is plays.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.choices(metric=[
        app_commands.Choice(name="plays", value=StatMetricType.PLAYS.value),
        app_commands.Choice(name="duration", value=StatMetricType.DURATION.value)
    ])
    async def active_platforms(self,
                               interaction: discord.Interaction,
                               days: int,
                               metric: discord.app_commands.Choice[str],
                               share: Optional[bool] = False) -> None:
        await self._build_and_send_response(
            interaction=interaction,
            stat_type=HomeStatType.TOP_PLATFORMS,
            metric=metric.value,
            days=days,
            name_key="platform",
            share=share
        )
