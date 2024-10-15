import discord

import consts
import modules.logs as logging
import modules.settings.models
from modules import emojis
from modules.discord import discord_utils
from modules.discord.models.tautulli_activity_summary import TautulliActivitySummary
from modules.emojis import EmojiManager
from modules.tasks.voice_category_stats import VoiceCategoryStatsMonitor
from modules.tautulli.tautulli_connector import TautulliConnector
from modules.versioning import VersionChecker


class ActivityStatsAndSummaryMessage(VoiceCategoryStatsMonitor):
    """
    A cron-based service loop that updates the live activity voice channel stats and summary text message.
    """

    def __init__(self,
                 discord_client,
                 settings: modules.settings.models.ActivityStats,
                 tautulli_connector: TautulliConnector,
                 guild_id: int,
                 message: discord.Message,
                 enable_stream_termination_if_possible: bool,
                 discord_status_settings: modules.settings.models.DiscordStatusMessage,
                 emoji_manager: EmojiManager,
                 version_checker: VersionChecker,
                 voice_category: discord.CategoryChannel = None):
        super().__init__(discord_client=discord_client,
                         guild_id=guild_id,
                         service_entrypoint=self.update_activity_details,
                         voice_category=voice_category)
        self.message = message
        self.enable_stream_termination_if_possible = enable_stream_termination_if_possible
        self.stats_settings = settings
        self.discord_status_settings = discord_status_settings
        self.tautulli = tautulli_connector
        self.emoji_manager = emoji_manager
        self.version_checker = version_checker

    async def update_activity_stats(self,
                                    summary: TautulliActivitySummary) -> None:

        logging.info("Updating activity stats...")

        # Only got here because activity stats are enabled, no need to check

        if self.stats_settings.plex_availability.enable:
            settings = self.stats_settings.plex_availability
            status_emoji = self.emoji_manager.get_emoji(key="online" if summary.plex_online else "offline")
            logging.debug(f"Updating {settings.name} voice channel with new status: {status_emoji}")
            await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                               stat=status_emoji)  # Always use an emoji for status

        activity = summary.activity

        # Only proceed if activity information was returned from Tautulli (Plex server could be offline)
        if activity:
            if self.stats_settings.stream_count.enable:
                settings = self.stats_settings.stream_count
                count = activity.stream_count
                logging.debug(f"Updating {settings.name} voice channel with new stream count: {count}")
                await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                                   stat=count)

            if self.stats_settings.transcode_count.enable:
                settings = self.stats_settings.transcode_count
                count = activity.transcode_count
                logging.debug(f"Updating {settings.name} voice channel with new transcode count: {count}")
                await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                                   stat=count)

            if self.stats_settings.bandwidth.enable:
                settings = self.stats_settings.bandwidth
                bandwidth = activity.total_bandwidth
                logging.debug(f"Updating {settings.name} voice channel with new bandwidth: {bandwidth}")
                await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                                   stat=bandwidth)

            if self.stats_settings.local_bandwidth.enable:
                settings = self.stats_settings.local_bandwidth
                bandwidth = activity.lan_bandwidth
                logging.debug(f"Updating {settings.name} voice channel with new local bandwidth: {bandwidth}")
                await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                                   stat=bandwidth)

            if self.stats_settings.remote_bandwidth.enable:
                settings = self.stats_settings.remote_bandwidth
                bandwidth = activity.wan_bandwidth
                logging.debug(f"Updating {settings.name} voice channel with new remote bandwidth: {bandwidth}")
                await self.edit_stat_voice_channel(voice_channel_settings=settings,
                                                   stat=bandwidth)

    async def add_stream_number_emoji_reactions(self,
                                                count: int,
                                                emoji_manager: EmojiManager):
        """
        Add reactions to a message for user interaction
        :param count: how many emojis to add
        :param emoji_manager: EmojiManager
        :return: None
        """
        # Only add reactions if necessary, and remove unnecessary reactions
        cache_msg = await self.message.channel.fetch_message(self.message.id)
        msg_emoji = [str(r.emoji) for r in cache_msg.reactions]

        # thanks twilsonco
        if count <= 0:
            if len(msg_emoji) > 0:
                await self.message.clear_reactions()
            return

        if count > emojis.max_controllable_stream_count_supported():
            logging.debug(
                f"""Tauticord supports controlling a maximum of {emojis.max_controllable_stream_count_supported()} streams.
            Stats will be displayed correctly, but any additional streams will not be able to be terminated.""")
            count = emojis.max_controllable_stream_count_supported()

        emoji_to_remove = []

        for i, e in enumerate(msg_emoji):
            if i >= count:  # ex. 5 streams, 6 reactions
                emoji_to_remove.append(e)
            elif not emoji_manager.is_valid_emoji_for_stream_number(emoji=e,
                                                                    number=i + 1):  # "6" emoji used for stream 5
                emoji_to_remove.append(e)

        # if all reactions need to be removed, do it all at once
        if len(emoji_to_remove) == len(msg_emoji):
            await self.message.clear_reactions()
            msg_emoji = []
        else:
            for e in emoji_to_remove:
                await self.message.clear_reaction(e)
                del (msg_emoji[msg_emoji.index(e)])

        for i in range(1, count + 1):
            emoji = emoji_manager.reaction_from_stream_number(i)
            if emoji not in msg_emoji:
                await self.message.add_reaction(emoji)

    async def update_activity_summary_message(self,
                                              summary: TautulliActivitySummary) -> None:
        """
        For performance and aesthetics, edit the old message if:
        1) the old message is the newest message in the channel, or
        2) if the only messages that are newer were written by this bot
        (which would be stream stop messages that have already been deleted)
        """
        await self.message.clear_reactions()

        if not summary.activity or summary.error_occurred:
            # error when refreshing Tautulli data, new_message is string (i.e. "Connection lost")
            logging.debug("Editing old message with Tautulli error...")
        else:
            logging.debug('Editing old message...')

        # update the message regardless of whether the content has changed
        self.message = await discord_utils.send_embed_message(embed=summary.embed, message=self.message)

        if self.tautulli.plex_pass_feature_is_allowed(feature=self.enable_stream_termination_if_possible,
                                                      warning="Stream termination control requires Plex Pass, ignoring setting..."):
            await self.add_stream_number_emoji_reactions(count=len(summary.streams),
                                                         emoji_manager=self.emoji_manager)
            # on_raw_reaction_add will handle the rest

    async def update_activity_details(self) -> None:
        """
        Collect new summary info, replace old message with new one (if enabled), update stats voice channels (if enabled)
        """

        embed_fields = []
        if self.version_checker.is_new_version_available():
            embed_fields.append(
                {"name": "🔔 New Version Available",
                 "value": f"A new version of Tauticord is available! [Click here]({consts.GITHUB_REPO_FULL_LINK}) to download it."})

        summary = self.tautulli.refresh_data(
            enable_stream_termination_if_possible=self.enable_stream_termination_if_possible,
            emoji_manager=self.emoji_manager, additional_embed_fields=embed_fields)

        if self.stats_settings.enable:
            await self.update_activity_stats(summary=summary)

        if self.discord_status_settings.should_update_with_activity:
            activity_name = self.discord_status_settings.activity_name
            message = self.discord_status_settings.message(stream_count=0)
            await discord_utils.update_presence(client=self.discord_client,
                                                activity_name=activity_name,
                                                line_one=message)

        if self.message:  # Set in the constructor, indicates that a summary message should be sent
            await self.update_activity_summary_message(summary=summary)
