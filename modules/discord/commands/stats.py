import os
from typing import Optional, Callable

import discord
from discord import app_commands
from discord.ext import commands

import modules.logs as logging
from modules import utils
from modules.charts import ChartMaker
from modules.tautulli.enums import StatChartType, StatMetricType, StatChartColors
from modules.tautulli.models.stats import PlayDurationStats, PlayCountStats
from modules.tautulli.tautulli_connector import (
    TautulliConnector,
)


class Stats(commands.GroupCog, name="stats"):
    def __init__(self, bot: commands.Bot, tautulli: TautulliConnector,
                 admin_check: Callable[[discord.Interaction], bool] = None):
        self.bot = bot
        self._tautulli = tautulli
        self._admin_check = admin_check
        super().__init__()  # This is required for the cog to work.
        logging.debug("Stats cog loaded.")

    async def check_admin(self, interaction: discord.Interaction) -> bool:
        if self._admin_check and not self._admin_check(interaction):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return False

        return True

    async def _build_and_send_response(self,
                                       interaction: discord.Interaction,
                                       chart_type: StatChartType,
                                       metric: StatMetricType,
                                       days: int,
                                       chart_builder_function: Callable[
                                           [PlayCountStats | PlayDurationStats, str], ChartMaker],
                                       username: str = None,
                                       share: Optional[bool] = False) -> None:
        passed_admin_check: bool = await self.check_admin(interaction)
        if not passed_admin_check:
            return

        user_id = None
        if username:
            user_id = self._tautulli.get_user_id_by_username(username=username)
            if not user_id:
                await interaction.response.send_message("User not found.", ephemeral=True)
                return

        stats = None
        match metric:
            case StatMetricType.PLAYS:
                stats: PlayCountStats | None = self._tautulli.get_play_count_chart_data(chart_type=chart_type,
                                                                                        days=days,
                                                                                        user_ids=[
                                                                                            str(user_id)] if user_id else None)
            case StatMetricType.DURATION:
                stats: PlayDurationStats | None = self._tautulli.get_play_duration_chart_data(chart_type=chart_type,
                                                                                              days=days,
                                                                                              user_ids=[
                                                                                                  str(user_id)] if user_id else None)

        if not stats:
            await interaction.response.send_message("No stats found.", ephemeral=True)
            return

        chart_title_metric: str = ""
        match metric:
            case StatMetricType.PLAYS:
                chart_title_metric: str = "play count"
            case StatMetricType.DURATION:
                chart_title_metric: str = "play duration"

        # Switch case setting the title_prefix based on the stat_type
        chart_title: str = ""
        match chart_type:
            case StatChartType.DAILY_BY_MEDIA_TYPE:
                chart_title: str = f"Daily {chart_title_metric} by media type"
            case StatChartType.BY_MONTH:
                chart_title: str = f"Total {chart_title_metric} by month"
            case StatChartType.BY_HOUR_OF_DAY:
                chart_title: str = f"{chart_title_metric} by hour of day"
            case StatChartType.BY_DAY_OF_WEEK:
                chart_title: str = f"{chart_title_metric} by day of week"
            case StatChartType.BY_TOP_10_PLATFORMS:
                chart_title: str = f"{chart_title_metric} by top 10 platforms"
            case StatChartType.BY_TOP_10_USERS:
                chart_title: str = f"{chart_title_metric} by top 10 users"

        chart_title: str = f"{chart_title} for past {days} {'day' if days == 1 else 'days'}"
        if username:
            chart_title: str = f"{chart_title} for {username}"

        chart_title: str = chart_title.title()

        chart_marker: ChartMaker = chart_builder_function(stats, chart_title)

        # TODO: Remove parent directory to use "/tmp" for temporary files in Docker
        # TODO: Add cron job to clean "/tmp" directory
        chart_path: str = utils.get_temporary_file_path(sub_directory="charts", parent_directory=os.getcwd(),
                                                        file_extension=".png")
        chart_marker.save(path=chart_path)

        await interaction.response.send_message(file=discord.File(chart_path), ephemeral=not share)

    @app_commands.command(name="graph-play-count-daily", description="Show graph of daily play count stats.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        username="The username of the user to show stats for. Leave blank for all users.",
    )
    async def graph_play_count_daily(self,
                                     interaction: discord.Interaction,
                                     days: int,
                                     username: Optional[str] = None,
                                     share: Optional[bool] = False) -> None:
        def chart_builder_function(stats: PlayCountStats, title: str) -> ChartMaker:
            tv_show_data = stats.tv_shows
            movie_data = stats.movies
            music_data = stats.music
            chart_maker = ChartMaker(x_axis=tv_show_data.x_axis, x_axis_labels=tv_show_data.x_axis,
                                     title=title, background_color=StatChartColors.BACKGROUND.value,
                                     text_color=StatChartColors.TEXT.value,
                                     grid_line_color=StatChartColors.GRIDLINES.value)
            # Order - Music, Movies, TV Shows
            chart_maker.add_line(values=music_data.values, label="Music", line_color=StatChartColors.MUSIC.value,
                                 text_color=StatChartColors.WHITE.value, marker="s")
            chart_maker.add_line(values=movie_data.values, label="Movies", line_color=StatChartColors.MOVIES.value,
                                 text_color=StatChartColors.WHITE.value, marker=">")
            chart_maker.add_line(values=tv_show_data.values, label="TV Shows", line_color=StatChartColors.TV.value,
                                 text_color=StatChartColors.WHITE.value, marker="o")

            return chart_maker

        await self._build_and_send_response(
            interaction=interaction,
            chart_type=StatChartType.DAILY_BY_MEDIA_TYPE,
            metric=StatMetricType.PLAYS,
            days=days,
            username=username,
            chart_builder_function=chart_builder_function,
            share=share
        )

    @app_commands.command(name="graph-play-count-day-of-week", description="Show graph of play count by day of week.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        username="The username of the user to show stats for. Leave blank for all users.",
    )
    async def graph_play_count_day_of_week(self,
                                           interaction: discord.Interaction,
                                           days: int,
                                           username: Optional[str] = None,
                                           share: Optional[bool] = False) -> None:
        def chart_builder_function(stats: PlayCountStats, title: str) -> ChartMaker:
            tv_show_data = stats.tv_shows
            movie_data = stats.movies
            music_data = stats.music
            chart_maker = ChartMaker(x_axis=stats.categories, x_axis_labels=stats.categories,
                                     title=title, background_color=StatChartColors.BACKGROUND.value,
                                     text_color=StatChartColors.TEXT.value,
                                     grid_line_color=StatChartColors.GRIDLINES.value)
            # Order - Music, Movies, TV Shows
            chart_maker.add_stacked_bar(values=[music_data.values, movie_data.values, tv_show_data.values],
                                        labels=["Music", "Movies", "TV"],
                                        bar_colors=[StatChartColors.MUSIC.value, StatChartColors.MOVIES.value,
                                                    StatChartColors.TV.value], bar_width=0.8,
                                        text_color=StatChartColors.BLACK.value)

            return chart_maker

        await self._build_and_send_response(
            interaction=interaction,
            chart_type=StatChartType.BY_DAY_OF_WEEK,
            metric=StatMetricType.PLAYS,
            days=days,
            username=username,
            chart_builder_function=chart_builder_function,
            share=share
        )

    @app_commands.command(name="graph-play-count-hour-of-day", description="Show graph of play count by hour of day.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        username="The username of the user to show stats for. Leave blank for all users.",
    )
    async def graph_play_count_hour_of_day(self,
                                           interaction: discord.Interaction,
                                           days: int,
                                           username: Optional[str] = None,
                                           share: Optional[bool] = False) -> None:
        def chart_builder_function(stats: PlayCountStats, title: str) -> ChartMaker:
            tv_show_data = stats.tv_shows
            movie_data = stats.movies
            music_data = stats.music
            chart_maker = ChartMaker(x_axis=stats.categories, x_axis_labels=stats.categories,
                                     title=title, background_color=StatChartColors.BACKGROUND.value,
                                     text_color=StatChartColors.TEXT.value,
                                     grid_line_color=StatChartColors.GRIDLINES.value)
            # Order - Music, Movies, TV Shows
            chart_maker.add_stacked_bar(values=[music_data.values, movie_data.values, tv_show_data.values],
                                        labels=["Music", "Movies", "TV"],
                                        bar_colors=[StatChartColors.MUSIC.value, StatChartColors.MOVIES.value,
                                                    StatChartColors.TV.value], bar_width=0.8,
                                        text_color=StatChartColors.BLACK.value)

            return chart_maker

        await self._build_and_send_response(
            interaction=interaction,
            chart_type=StatChartType.BY_HOUR_OF_DAY,
            metric=StatMetricType.PLAYS,
            days=days,
            username=username,
            chart_builder_function=chart_builder_function,
            share=share
        )

    @app_commands.command(name="graph-play-count-platforms",
                          description="Show graph of play count by top 10 platforms.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        username="The username of the user to show stats for. Leave blank for all users.",
    )
    async def graph_play_count_platforms(self,
                                         interaction: discord.Interaction,
                                         days: int,
                                         username: Optional[str] = None,
                                         share: Optional[bool] = False) -> None:
        def chart_builder_function(stats: PlayCountStats, title: str) -> ChartMaker:
            tv_show_data = stats.tv_shows
            movie_data = stats.movies
            music_data = stats.music
            chart_maker = ChartMaker(x_axis=stats.categories, x_axis_labels=stats.categories,
                                     title=title, background_color=StatChartColors.BACKGROUND.value,
                                     text_color=StatChartColors.TEXT.value,
                                     grid_line_color=StatChartColors.GRIDLINES.value)
            # Order - Music, Movies, TV Shows
            chart_maker.add_stacked_bar(values=[music_data.values, movie_data.values, tv_show_data.values],
                                        labels=["Music", "Movies", "TV"],
                                        bar_colors=[StatChartColors.MUSIC.value, StatChartColors.MOVIES.value,
                                                    StatChartColors.TV.value], bar_width=0.8,
                                        text_color=StatChartColors.BLACK.value)

            return chart_maker

        await self._build_and_send_response(
            interaction=interaction,
            chart_type=StatChartType.BY_TOP_10_PLATFORMS,
            metric=StatMetricType.PLAYS,
            days=days,
            username=username,
            chart_builder_function=chart_builder_function,
            share=share
        )

    @app_commands.command(name="graph-play-count-users", description="Show graph of play count by top 10 users.")
    @app_commands.describe(
        days="The number of past days to show stats for.",
        username="The username of the user to show stats for. Leave blank for all users.",
    )
    async def graph_play_count_users(self,
                                     interaction: discord.Interaction,
                                     days: int,
                                     username: Optional[str] = None,
                                     share: Optional[bool] = False) -> None:
        def chart_builder_function(stats: PlayCountStats, title: str) -> ChartMaker:
            tv_show_data = stats.tv_shows
            movie_data = stats.movies
            music_data = stats.music
            chart_maker = ChartMaker(x_axis=stats.categories, x_axis_labels=stats.categories,
                                     title=title, background_color=StatChartColors.BACKGROUND.value,
                                     text_color=StatChartColors.TEXT.value,
                                     grid_line_color=StatChartColors.GRIDLINES.value)
            # Order - Music, Movies, TV Shows
            chart_maker.add_stacked_bar(values=[music_data.values, movie_data.values, tv_show_data.values],
                                        labels=["Music", "Movies", "TV"],
                                        bar_colors=[StatChartColors.MUSIC.value, StatChartColors.MOVIES.value,
                                                    StatChartColors.TV.value], bar_width=0.8,
                                        text_color=StatChartColors.BLACK.value)

            return chart_maker

        await self._build_and_send_response(
            interaction=interaction,
            chart_type=StatChartType.BY_TOP_10_USERS,
            metric=StatMetricType.PLAYS,
            days=days,
            username=username,
            chart_builder_function=chart_builder_function,
            share=share
        )

    # TODO: Add play duration stats commands