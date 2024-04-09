import asyncio

import discord

import modules.logs as logging
import modules.settings.models as settings_models
import modules.tautulli.tautulli_connector
from modules import versioning
from modules.analytics import GoogleAnalytics
from modules.discord import discord_utils
from modules.discord.services.base_service import BaseService
from modules.emojis import EmojiManager
from modules.errors import TauticordSetupFailure
from modules.tasks.activity import ActivityStatsAndSummaryMessage
from modules.utils import quote


class LiveActivityMonitor(BaseService):
    """
    A service that monitors live activity on the Discord server. Starts running when the bot is ready.
    """

    def __init__(self,
                 tautulli_connector: modules.tautulli.tautulli_connector.TautulliConnector,
                 discord_settings: settings_models.Discord,
                 tautulli_settings: settings_models.Tautulli,
                 stats_settings: settings_models.Stats,
                 emoji_manager: EmojiManager,
                 analytics: GoogleAnalytics,
                 version_checker: versioning.VersionChecker):
        super().__init__()
        self.tautulli: modules.tautulli.tautulli_connector.TautulliConnector = tautulli_connector
        self.guild_id: int = discord_settings.server_id
        self.admin_ids: list[int] = discord_settings.admin_ids
        self.refresh_time: int = tautulli_settings.refresh_interval_seconds
        self.use_summary_message: bool = discord_settings.use_summary_message
        self.stats_settings: settings_models.Stats = stats_settings
        self.emoji_manager: EmojiManager = emoji_manager
        self.version_checker: versioning.VersionChecker = version_checker
        self.analytics: GoogleAnalytics = analytics
        self.discord_status_settings: settings_models.DiscordStatusMessage = discord_settings.status_message_settings
        self.tautulli_summary_channel_name: str = discord_settings.channel_name

        self.tautulli_summary_channel: discord.TextChannel = None
        self.activity_monitor: ActivityStatsAndSummaryMessage = None

    async def associate_bot_callbacks(self):
        # noinspection PyAttributeOutsideInit
        self.on_raw_reaction_add = self.bot.event(self.on_raw_reaction_add)

    async def enabled(self) -> bool:
        # Enable if voice channel activity stats are enabled and/or if the summary message is enabled
        return self.stats_settings.activity.enable or self.use_summary_message

    async def on_ready(self):
        logging.info("Loading Tautulli summary service...")

        # Prepare the summary message to be used for activity stats if enabled
        summary_message = None
        if self.use_summary_message:
            logging.info("Loading Tautulli text channel settings...")

            self.tautulli_summary_channel: discord.TextChannel = \
                await discord_utils.get_or_create_discord_channel_by_name(
                    client=self.bot,
                    guild_id=self.guild_id,
                    channel_name=self.tautulli_summary_channel_name,
                    channel_type=discord.ChannelType.text)
            if not self.tautulli_summary_channel:
                raise Exception(f"Could not load {quote(self.tautulli_summary_channel_name)} channel. Exiting...")

            logging.debug(f"{quote(self.tautulli_summary_channel_name)} channel collected.")

            # If the very last message in the channel is from Tauticord, use it
            async for msg in self.tautulli_summary_channel.history(limit=1):
                if msg.author == self.bot.user:
                    await msg.clear_reactions()

                    # Store the message
                    summary_message = msg
                    break

            # If the very last message in the channel is not from Tauticord, make a new one.
            if not summary_message:
                logging.info("Couldn't find old message, sending initial message...")
                embed = discord.Embed(title="Welcome to Tauticord!")
                embed.add_field(name="Starting up...",
                                value='This will be replaced once we get data.',
                                inline=False)
                summary_message = await discord_utils.send_embed_message(embed=embed,
                                                                         channel=self.tautulli_summary_channel)

            if not summary_message:
                raise TauticordSetupFailure("Could not prepare activity summary message")

            # Start the version checking service if enabled (to add to the summary message)
            if self.version_checker and self.version_checker.enable:
                logging.info("Starting version checking service...")
                # noinspection PyAsyncCall
                asyncio.create_task(self.version_checker.monitor_for_new_version())

        # Prepare the voice category for activity stats if enabled
        activity_stats_voice_category = None
        if self.stats_settings.activity.enable:
            logging.info("Loading Tautulli activity stats settings...")
            activity_stats_voice_category = await self.collect_discord_voice_category(
                guild_id=self.guild_id,
                category_name=self.stats_settings.activity.category_name)

        # Run the activity stats updater
        # minimum 5-second sleep time hard-coded, trust me, don't DDoS your server
        refresh_time = max([5, self.refresh_time])
        # This handles both text channel updates AND activity stats voice channel updates
        self.activity_monitor = ActivityStatsAndSummaryMessage(discord_client=self.bot,
                                                               settings=self.stats_settings.activity,
                                                               discord_status_settings=self.discord_status_settings,
                                                               tautulli_connector=self.tautulli,
                                                               guild_id=self.guild_id,
                                                               message=summary_message,
                                                               emoji_manager=self.emoji_manager,
                                                               version_checker=self.version_checker,
                                                               voice_category=activity_stats_voice_category)
        # noinspection PyAsyncCall
        # Want the service to run even if the voice channel is not found (e.g. text summary only)
        asyncio.create_task(self.activity_monitor.run_service(interval_seconds=refresh_time,
                                                              override_voice_channel_check=True))

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if not self.tautulli_summary_channel or not self.activity_monitor:
            return

        emoji = payload.emoji
        user_id = payload.user_id
        message = await self.tautulli_summary_channel.fetch_message(payload.message_id)
        reaction_type = "REACTION_ADD"

        if discord_utils.is_valid_reaction(reaction_emoji=emoji,
                                           reaction_user_id=user_id,
                                           reaction_message=message,
                                           reaction_type=reaction_type,
                                           valid_message=self.activity_monitor.message,
                                           valid_reaction_type=None,  # We already know it's the right type
                                           valid_emojis=self.emoji_manager.stream_number_emojis,
                                           valid_user_ids=self.admin_ids):
            # message here will be the current message, so we can just use that
            end_notification = await self.stop_tautulli_stream_via_reaction_emoji(emoji=emoji, message=message)
            if end_notification:
                await end_notification.delete(delay=5)  # delete after 5 seconds

    async def stop_tautulli_stream_via_reaction_emoji(self, emoji: discord.PartialEmoji, message: discord.Message) -> \
            discord.Message:
        stream_number: int = self.emoji_manager.stream_number_from_emoji(emoji=emoji)

        logging.debug(f"Stopping stream {emoji}...")
        stopped_message = self.tautulli.stop_stream(emoji=emoji, stream_number=stream_number)
        logging.info(stopped_message)
        end_notification = await self.tautulli_summary_channel.send(content=stopped_message)
        await message.clear_reaction(str(emoji))
        return end_notification
