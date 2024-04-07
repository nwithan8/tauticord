import asyncio

import modules.logs as logging
import modules.settings.models as settings_models
import modules.tautulli.tautulli_connector
from modules.analytics import GoogleAnalytics
from modules.discord.services.base_service import BaseService
from modules.emojis import EmojiManager
from modules.tasks.performance_stats import PerformanceMonitor


class PerformanceStatsMonitor(BaseService):
    """
    A service that monitors performance statistics and sends them to Discord. Starts running when the bot is ready.
    """

    def __init__(self,
                 tautulli_connector: modules.tautulli.tautulli_connector.TautulliConnector,
                 discord_settings: settings_models.Discord,
                 stats_settings: settings_models.Stats,
                 run_args_settings: settings_models.RunArgs,
                 emoji_manager: EmojiManager,
                 analytics: GoogleAnalytics):
        super().__init__()
        self.tautulli: modules.tautulli.tautulli_connector.TautulliConnector = tautulli_connector
        self.guild_id: int = discord_settings.server_id
        self.run_args_settings: settings_models.RunArgs = run_args_settings
        self.stats_settings: settings_models.Stats = stats_settings
        self.emoji_manager: EmojiManager = emoji_manager
        self.analytics: GoogleAnalytics = analytics

        self.performance_stats_monitor: PerformanceMonitor = None

    async def enabled(self) -> bool:
        return self.stats_settings.performance.enable

    async def on_ready(self):
        logging.info("Starting performance monitoring service...")
        voice_category = await self.collect_discord_voice_category(
            guild_id=self.guild_id,
            category_name=self.stats_settings.performance.category_name)
        # Hard-coded 5-minute refresh time
        refresh_time = 5 * 60
        self.performance_stats_monitor = PerformanceMonitor(discord_client=self.bot,
                                                            settings=self.stats_settings.performance,
                                                            tautulli_connector=self.tautulli,
                                                            run_args_settings=self.run_args_settings,
                                                            guild_id=self.guild_id,
                                                            voice_category=voice_category)
        # noinspection PyAsyncCall
        asyncio.create_task(self.performance_stats_monitor.run_service(interval_seconds=refresh_time))
