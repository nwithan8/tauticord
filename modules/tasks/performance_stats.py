from typing import List

import discord
import plexapi.server

import modules.logs as logging
import modules.settings.models
from modules import system_stats
from modules.tasks.voice_category_stats import VoiceCategoryStatsMonitor
from modules.tautulli.tautulli_connector import TautulliConnector
from modules.utils import quote


class PerformanceMonitor(VoiceCategoryStatsMonitor):
    """
    A cron-based service loop that updates the performance stats voice channels.
    """

    def __init__(self,
                 discord_client,
                 settings: modules.settings.models.PerformanceStats,
                 run_args_settings: modules.settings.models.RunArgs,
                 tautulli_connector: TautulliConnector,
                 guild_id: int,
                 voice_category: discord.CategoryChannel = None):
        super().__init__(discord_client=discord_client,
                         guild_id=guild_id,
                         service_entrypoint=self.update_performance_stats,
                         voice_category=voice_category)
        self.stats_settings = settings
        self.run_args_settings = run_args_settings
        self.tautulli = tautulli_connector

    def calculate_cpu_percent(self) -> str:
        if not self.tautulli.plex_api:
            logging.error("No Plex API found to monitor CPU usage.")
            return "N/A"

        resources: List[plexapi.server.StatisticsResources] = self.tautulli.plex_api.resources()

        if not resources:
            logging.error("Could not load CPU usage from Plex API.")
            return "N/A"

        # Get the last resource (most recent)
        resource = resources[-1]
        # Process - Plex Media Server, Host - Host
        return f"{resource.processCpuUtilization:.2f}%"  # 0.00%

    def calculate_memory_percent(self) -> str:
        if not self.tautulli.plex_api:
            logging.error("No Plex API found to monitor RAM usage.")
            return "N/A"

        resources: List[plexapi.server.StatisticsResources] = self.tautulli.plex_api.resources()

        if not resources:
            logging.error("Could not load RAM usage from Plex API.")
            return "N/A"

        # Get the last resource (most recent)
        resource = resources[-1]
        # Process - Plex Media Server, Host - Host
        return f"{resource.processMemoryUtilization:.2f}%"  # 0.00%

    def calculate_disk_usage(self) -> str:
        path = self.run_args_settings.performance_disk_space_mapping
        if not system_stats.path_exists(path):
            logging.error(f"Could not find {quote(path)} to monitor disk space.")
            return "N/A"
        else:
            return system_stats.disk_usage_display(path)

    async def update_performance_stats(self) -> None:
        logging.info("Updating performance stats...")

        # Only got here because performance stats are enabled, no need to check

        if self.stats_settings.user_count.enable:
            settings = self.stats_settings.user_count
            user_count = self.tautulli.get_user_count()
            logging.debug(f"Updating Users voice channel with new user count: {user_count}")
            await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                               stat=user_count)

        if self.stats_settings.disk.enable:
            settings = self.stats_settings.disk
            stat = self.calculate_disk_usage()
            logging.debug(f"Updating Disk voice channel with new disk space: {stat}")
            await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                               stat=stat)

        if self.stats_settings.cpu.enable:
            settings = self.stats_settings.cpu
            cpu_percent = self.calculate_cpu_percent()
            logging.debug(f"Updating CPU voice channel with new CPU percent: {cpu_percent}")
            await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                               stat=cpu_percent)

        if self.stats_settings.memory.enable:
            settings = self.stats_settings.memory
            memory_percent = self.calculate_memory_percent()
            logging.debug(f"Updating Memory voice channel with new Memory percent: {memory_percent}")
            await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                               stat=memory_percent)
