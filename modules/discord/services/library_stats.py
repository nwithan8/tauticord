import asyncio

import modules.logs as logging
import modules.settings.models as settings_models
import modules.tautulli.tautulli_connector
from modules.analytics import GoogleAnalytics
from modules.discord.services.base_service import BaseService
from modules.emojis import EmojiManager
from modules.tasks.library_stats import LibraryStats


class LibraryStatsMonitor(BaseService):
    """
    A service that monitors library statistics and sends them to Discord. Starts running when the bot is ready.
    """

    def __init__(self,
                 tautulli_connector: modules.tautulli.tautulli_connector.TautulliConnector,
                 discord_settings: settings_models.Discord,
                 stats_settings: settings_models.Stats,
                 emoji_manager: EmojiManager,
                 analytics: GoogleAnalytics):
        super().__init__()
        self.tautulli: modules.tautulli.tautulli_connector.TautulliConnector = tautulli_connector
        self.guild_id: int = discord_settings.server_id
        self.library_refresh_time: int = stats_settings.library.refresh_interval_seconds
        self.stats_settings: settings_models.Stats = stats_settings
        self.emoji_manager: EmojiManager = emoji_manager
        self.analytics: GoogleAnalytics = analytics

        self.library_stats_monitor: LibraryStats = None

    async def enabled(self) -> bool:
        return self.stats_settings.library.enable

    async def on_ready(self):
        logging.info("Starting Tautulli library stats service...")
        voice_category = await self.collect_discord_voice_category(
            guild_id=self.guild_id,
            category_name=self.stats_settings.library.category_name)
        # minimum 5-minute sleep time hard-coded, trust me, don't DDoS your server
        refresh_time = max([5 * 60,
                            self.library_refresh_time])
        self.library_stats_monitor = LibraryStats(discord_client=self.bot,
                                                  settings=self.stats_settings.library,
                                                  tautulli_connector=self.tautulli,
                                                  guild_id=self.guild_id,
                                                  voice_category=voice_category)
        # noinspection PyAsyncCall
        asyncio.create_task(self.library_stats_monitor.run_service_override(interval_seconds=refresh_time))
