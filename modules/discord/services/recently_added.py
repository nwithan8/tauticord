import asyncio

import discord

import modules.logs as logging
import modules.settings.models as settings_models
import modules.tautulli.tautulli_connector
from modules.analytics import GoogleAnalytics
from modules.discord import discord_utils
from modules.discord.enums import AnnouncementMessageType
from modules.discord.services.base_service import BaseService
from modules.emojis import EmojiManager
from modules.errors import TauticordSetupFailure
from modules.tasks.recently_added_carousel import RecentlyAddedCarouselMonitor
from modules.utils import quote


class RecentlyAddedMonitor(BaseService):
    """
    A service that monitors recently-added items in Tautulli and displays them in the Discord server. Starts running when the bot is ready.
    """

    def __init__(self,
                 tautulli_connector: modules.tautulli.tautulli_connector.TautulliConnector,
                 discord_settings: settings_models.Discord,
                 tautulli_settings: settings_models.Tautulli,
                 emoji_manager: EmojiManager,
                 analytics: GoogleAnalytics):
        super().__init__()
        self.tautulli: modules.tautulli.tautulli_connector.TautulliConnector = tautulli_connector
        self.guild_id: int = discord_settings.server_id
        self.refresh_time: int = tautulli_settings.refresh_interval_seconds
        self.use_recently_added_carousel_message: bool = discord_settings.use_recently_added_carousel_message
        self.emoji_manager: EmojiManager = emoji_manager
        self.analytics: GoogleAnalytics = analytics
        self.discord_status_settings: settings_models.DiscordStatusMessage = discord_settings.status_message_settings
        self.tautulli_announcements_channel_name: str = discord_settings.announcements_channel_name

        self.tautulli_announcements_channel: discord.TextChannel = None
        self.recently_added_carousel_monitor: RecentlyAddedCarouselMonitor = None

    async def enabled(self) -> bool:
        # Enable if announcements channel is enabled and the recently-added summary message is enabled
        return self.tautulli_announcements_channel_name and self.use_recently_added_carousel_message

    async def on_ready(self):
        logging.info("Loading recently-added service...")

        # Prepare the summary message to be used for activity stats if enabled
        recently_added_message = None
        if self.use_recently_added_carousel_message:
            logging.info("Loading Tautulli text channel settings...")

            self.tautulli_announcements_channel: discord.TextChannel = \
                await discord_utils.get_or_create_discord_channel_by_name(
                    client=self.bot,
                    guild_id=self.guild_id,
                    channel_name=self.tautulli_announcements_channel_name,
                    channel_type=discord.ChannelType.text)
            if not self.tautulli_announcements_channel:
                raise Exception(f"Could not load {quote(self.tautulli_announcements_channel_name)} channel. Exiting...")

            logging.debug(f"{quote(self.tautulli_announcements_channel_name)} channel collected.")

            footer_text = AnnouncementMessageType.get_footer(
                announcement_message_type=AnnouncementMessageType.RECENTLY_ADDED_POSTERS)

            # Retrieve the most recent "recently added" embed message from the announcements channel, if it exists
            recently_added_message = await discord_utils.get_most_recent_message_in_channel_matching_validators(
                channel=self.tautulli_announcements_channel,
                validators=[
                    lambda m: m.author == self.bot.user,
                    lambda m: len(m.embeds) > 0,
                    lambda m: any(e.footer.text.startswith(footer_text) for e in m.embeds if e.footer and e.footer.text)
                ])
            if recently_added_message:
                logging.info("Found existing recently added message")
                await recently_added_message.clear_reactions()  # Might as well, doesn't actually affect anything
            else:
                # If we could not find an existing recently added message, create a new one
                logging.info("Couldn't find old recently added message, sending initial message...")
                embed = discord.Embed(title="Recently Added")
                embed.add_field(name="Starting up...",
                                value='This will be replaced once we get data.',
                                inline=False)
                embed.set_footer(text=footer_text)
                recently_added_message = await discord_utils.send_embed_message(embed=embed,
                                                                                channel=self.tautulli_announcements_channel)
            if not recently_added_message:
                raise TauticordSetupFailure("Could not prepare recently added message")

        # Run the activity stats updater
        # Hard-coded 5-minute refresh time (will annoy users if they're in the middle of scrolling through and it constantly refreshes/resets)
        refresh_time = 5 * 60
        self.recently_added_carousel_monitor = RecentlyAddedCarouselMonitor(
            discord_client=self.bot,
            tautulli_connector=self.tautulli,
            guild_id=self.guild_id,
            message=recently_added_message,
            text_channel=self.tautulli_announcements_channel
        )
        # noinspection PyAsyncCall
        asyncio.create_task(self.recently_added_carousel_monitor.run_service(interval_seconds=refresh_time))
