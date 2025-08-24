import discord

from modules.discord.views import PaginatedCardView, PaginatedViewStyle, ButtonColor, PaginatedCardViewItem, EmbedColor
from modules.tautulli.models.recently_added_media_item import RecentlyAddedMediaItem


class RecentlyAddedMediaItemCard(PaginatedCardViewItem):
    def __init__(self, item: RecentlyAddedMediaItem, footer: str = None):
        self._item = item
        self._footer = footer

    def render(self) -> discord.Embed:
        embed = discord.Embed(
            title=self._item.title,
            color=EmbedColor.DARK_ORANGE.value)
        if self._footer:
            embed.set_footer(text=self._footer)

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


class RecentlyAddedSummaryView(PaginatedCardView):
    def __init__(self, items: list[RecentlyAddedMediaItem], footer: str = None):
        cards = [RecentlyAddedMediaItemCard(item=item, footer=footer) for item in items]

        style = PaginatedViewStyle()
        style.to_beginning_button_color = ButtonColor.GREEN
        style.to_end_button_color = ButtonColor.GREEN
        style.previous_button_color = ButtonColor.BLURPLE
        style.next_button_color = ButtonColor.BLURPLE

        super().__init__(cards=cards, title="Recently Added Media", style=style)
