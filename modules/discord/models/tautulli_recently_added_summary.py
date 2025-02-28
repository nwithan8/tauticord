from typing import List

import discord

from modules.discord import discord_utils
from modules.discord.views.recently_added_summary import RecentlyAddedSummaryView
from modules.tautulli.models.recently_added_media_item import RecentlyAddedMediaItem


# This data comes from querying the Tautulli API for the X most recently added items
# This is DIFFERENT from the webhooks that help us track HOW MANY items were added in the last X minutes

class TautulliRecentlyAddedSummary:
    def __init__(self,
                 items: List[RecentlyAddedMediaItem]):
        self.items = items or []

    # This is for replying to a slash command with the summary view
    async def reply_to_slash_command(self, interaction: discord.Interaction, ephemeral: bool = False) -> None:
        if not self.items:
            await discord_utils.respond_to_slash_command_with_text(interaction=interaction,
                                                                   text="No recently added items found.",
                                                                   ephemeral=True)  # Always ephemeral if error
            return

        view = RecentlyAddedSummaryView(items=self.items)

        # Handles sending the message and updating the embed when interacted with
        await view.respond_to_slash_command(interaction=interaction, ephemeral=ephemeral)

    # This is for sending/editing a message in a channel with the summary view
    async def send_to_channel(self, message: discord.Message) -> discord.Message:
        if not self.items:
            return await message.channel.send("No recently added items found.")

        view = RecentlyAddedSummaryView(items=self.items)

        # Handles sending the message and updating the embed when interacted with
        return await view.send_to_channel(message=message)
