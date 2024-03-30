import discord

import modules.logs as logging
import modules.settings.models
from modules import system_stats
from modules.tasks.voice_category_stats import VoiceCategoryStatsMonitor
from modules.tautulli.tautulli_connector import TautulliConnector
from modules.utils import quote


class PerformanceMonitor(VoiceCategoryStatsMonitor):
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

    async def update_performance_stats(self) -> None:
        logging.info("Updating performance stats...")

        # Only got here because performance stats are enabled, no need to check

        if self.stats_settings.user_count.enable:
            settings = self.stats_settings.user_count
            user_count = self.tautulli.get_user_count()
            logging.info(f"Updating Users voice channel with new user count: {user_count}")
            await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                               stat=user_count)

        if self.stats_settings.disk.enable:
            settings = self.stats_settings.disk
            path = self.run_args_settings.performance_disk_space_mapping
            if not system_stats.path_exists(path):
                logging.error(f"Could not find {quote(path)} to monitor disk space.")
                stat = "N/A"
            else:
                stat = system_stats.disk_usage_display(path)

            logging.info(f"Updating Disk voice channel with new disk space: {stat}")
            await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                               stat=stat)

        if self.stats_settings.cpu.enable:
            settings = self.stats_settings.cpu
            cpu_percent = system_stats.cpu_usage_display()
            logging.info(f"Updating CPU voice channel with new CPU percent: {cpu_percent}")
            await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                               stat=cpu_percent)

        if self.stats_settings.memory.enable:
            settings = self.stats_settings.memory
            memory_percent = system_stats.ram_usage_display()
            logging.info(f"Updating Memory voice channel with new Memory percent: {memory_percent}")
            await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                               stat=memory_percent)
