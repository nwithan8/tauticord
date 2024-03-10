from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import modules.logs as logging
from modules.discord.commands._base import (
    respond_thinking,
)
from modules.discord.views import (
    ButtonColor,
    EmbedColor,
    PaginatedViewStyle,
    PaginatedCardView,
    PaginatedCardViewItem
)
from modules.tautulli.tautulli_connector import (
    TautulliConnector,
    RecentlyAddedMediaItem,
)


def _build_top_media_response_embed(stats: list[dict[str, str]], title: str) -> discord.Embed:
    embed = discord.Embed(title=title, color=EmbedColor.DARK_ORANGE.value)
    for stat in stats:
        embed.add_field(name=stat["title"], value=stat["total_plays"], inline=False)
    return embed


def _build_top_user_response_embed(stats: list[dict[str, str]], title: str) -> discord.Embed:
    embed = discord.Embed(title=title, color=EmbedColor.DARK_ORANGE.value)
    for stat in stats:
        embed.add_field(name=stat["friendly_name"], value=stat["total_plays"], inline=False)
    return embed


class RecentlyAddedMediaItemCard(PaginatedCardViewItem):
    def __init__(self, item: RecentlyAddedMediaItem):
        self._item = item

    def render(self) -> discord.Embed:
        embed = discord.Embed(
            title=self._item.title,
            color=EmbedColor.DARK_ORANGE.value)

        summary = self._item.summary
        if not summary:
            summary = "No summary available."
        if len(summary) > 1024:
            summary = summary[:1021] + "..."
        embed.add_field(name="Summary", value=summary, inline=False)

        embed.add_field(name="Available In", value=self._item.library, inline=False)
        embed.add_field(name=f"Watch Now", value=f"[Open in Plex Web]({self._item.link})", inline=False)

        embed.set_image(url=self._item.poster_url)

        return embed


class Recently(commands.GroupCog, name="recently"):
    def __init__(self, bot: commands.Bot, tautulli: TautulliConnector):
        self.bot = bot
        self._tautulli = tautulli
        super().__init__()  # This is required for the cog to work.
        logging.info("Recently cog loaded.")

    @app_commands.command(name="added", description="Show recently added media.")
    @app_commands.describe(
        media_type="The type of media to filter by.",
        share="Whether to make the response visible to the channel."
    )
    @app_commands.rename(media_type="media-type")
    @app_commands.choices(
        media_type=[
            discord.app_commands.Choice(name="Movies", value="movie"),
            discord.app_commands.Choice(name="Shows", value="show"),
        ]
    )
    async def added(self, interaction: discord.Interaction,
                    media_type: Optional[discord.app_commands.Choice[str]] = None,
                    share: Optional[bool] = False) -> None:
        # Defer the response to give more than the default 3 seconds to respond.
        await respond_thinking(interaction=interaction, ephemeral=not share)

        limit = 5
        if media_type:
            media_type = media_type.value

        items = self._tautulli.get_recently_added_media(count=limit, media_type=media_type)
        if not items:
            await interaction.response.send_message("No recently added items found.", ephemeral=True)
            return

        cards = [RecentlyAddedMediaItemCard(item=item) for item in items]

        style = PaginatedViewStyle()
        style.to_beginning_button_color = ButtonColor.GREEN
        style.to_end_button_color = ButtonColor.GREEN
        style.previous_button_color = ButtonColor.BLURPLE
        style.next_button_color = ButtonColor.BLURPLE

        paginated_view = PaginatedCardView(cards=cards, title="Recently Added Media", style=style)

        await paginated_view.send(interaction=interaction, ephemeral=not share)
