import discord

import modules.logs as logging
from modules.discord.enums import AnnouncementMessageType
from modules.discord.models.tautulli_recently_added_summary import TautulliRecentlyAddedSummary

from modules.tasks.base import TextChannelMessageMonitor
from modules.tautulli.tautulli_connector import TautulliConnector


class RecentlyAddedCarouselMonitor(TextChannelMessageMonitor):
    """
    A cron-based service loop that updates the recently-added poster carousel message.
    """

    def __init__(self,
                 discord_client,
                 tautulli_connector: TautulliConnector,
                 guild_id: int,
                 message: discord.Message,
                 text_channel: discord.TextChannel = None):
        super().__init__(discord_client=discord_client,
                         guild_id=guild_id,
                         service_entrypoint=self.update_recently_added_carousel_message,
                         text_channel=text_channel)
        self.message = message
        self.tautulli = tautulli_connector

    async def update_recently_added_carousel_message(self) -> None:
        logging.info("Updating recently-added carousel message...")

        footer_text = AnnouncementMessageType.get_footer(
            announcement_message_type=AnnouncementMessageType.RECENTLY_ADDED_POSTERS)

        summary: TautulliRecentlyAddedSummary = self.tautulli.get_recently_added_media_summary(count=5, # Most recent 5 items of any media type (movies, shows, albums, etc.)
                                                                                               footer=footer_text)  # Tag with footer for lookup during bot boot
        await summary.send_to_channel(message=self.message)

