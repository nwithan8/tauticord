import enum

import discord

import modules.logs as logging
from modules.discord import discord_utils


class EmbedColor(enum.Enum):
    DEFAULT = discord.Color.default()
    TEAL = discord.Color.teal()
    DARK_TEAL = discord.Color.dark_teal()
    GREEN = discord.Color.green()
    DARK_GREEN = discord.Color.dark_green()
    BLUE = discord.Color.blue()
    DARK_BLUE = discord.Color.dark_blue()
    PURPLE = discord.Color.purple()
    DARK_PURPLE = discord.Color.dark_purple()
    MAGENTA = discord.Color.magenta()
    DARK_MAGENTA = discord.Color.dark_magenta()
    GOLD = discord.Color.gold()
    DARK_GOLD = discord.Color.dark_gold()
    ORANGE = discord.Color.orange()
    DARK_ORANGE = discord.Color.dark_orange()
    RED = discord.Color.red()
    DARK_RED = discord.Color.dark_red()
    LIGHT_GREY = discord.Color.light_grey()
    DARK_GREY = discord.Color.dark_grey()
    LIGHTER_GREY = discord.Color.lighter_grey()
    DARKER_GREY = discord.Color.darker_grey()
    BLURPLE = discord.Color.blurple()
    GREYPLE = discord.Color.greyple()


class ButtonColor(enum.Enum):
    PRIMARY = discord.ButtonStyle.primary
    SECONDARY = discord.ButtonStyle.secondary
    SUCCESS = discord.ButtonStyle.success
    DANGER = discord.ButtonStyle.danger
    LINK = discord.ButtonStyle.link
    RED = discord.ButtonStyle.red
    GREEN = discord.ButtonStyle.green
    GREY = discord.ButtonStyle.grey
    BLURPLE = discord.ButtonStyle.blurple
    DISABLED = discord.ButtonStyle.grey


class PaginatedViewStyle:
    to_beginning_button_label = "|<"
    to_beginning_button_color = ButtonColor.PRIMARY
    to_beginning_button_color_disabled = ButtonColor.DISABLED
    to_end_button_label = ">|"
    to_end_button_color = ButtonColor.PRIMARY
    to_end_button_color_disabled = ButtonColor.DISABLED
    previous_button_label = "<"
    previous_button_color = ButtonColor.PRIMARY
    previous_button_color_disabled = ButtonColor.DISABLED
    next_button_label = ">"
    next_button_color = ButtonColor.PRIMARY
    next_button_color_disabled = ButtonColor.DISABLED


class PaginatedView(discord.ui.View):
    def __init__(self, title: str, include_page_progress_in_title: bool = True,
                 starting_page_number: int = 1, style: PaginatedViewStyle = None):
        super().__init__()
        self._title = title
        self._include_page_progress_in_title = include_page_progress_in_title
        self._current_page_number = starting_page_number
        self._style = style if style else PaginatedViewStyle()
        self._message = None

    def get_total_page_count(self) -> int:
        """
        Override this method to return the total number of pages.
        """
        return 1

    def render(self, page_number: int) -> discord.Embed:
        """
        Override this method to return the content for a specific page.
        """
        return discord.Embed(title=self._title)

    async def respond_to_slash_command(self, interaction: discord.Interaction, ephemeral: bool = False):
        self._message = await discord_utils.respond_to_slash_command_with_view(interaction=interaction,
                                                                               view=self,
                                                                               ephemeral=ephemeral)

        # Need to immediately update the message to set the initial embed
        await self.update_message()

    async def send_to_channel(self, message: discord.Message) -> discord.Message:
        self._message = message
        self._message = await discord_utils.send_view_message(message=self._message, view=self)

        # Need to immediately update the message to set the initial embed
        await self.update_message()

        return self._message

    async def update_message(self):
        if not self._message:
            logging.error("Message not set.")

        self.update_buttons()

        embed = self.render(page_number=self._current_page_number)

        await self._message.edit(embed=embed, view=self)

    def update_buttons(self):
        if self._current_page_number == 1:
            self.first.disabled = True
            self.first.style = self._style.to_beginning_button_color_disabled.value
            self.previous.disabled = True
            self.previous.style = self._style.previous_button_color_disabled.value
        else:
            self.first.disabled = False
            self.first.style = self._style.to_beginning_button_color.value
            self.previous.disabled = False
            self.previous.style = self._style.previous_button_color.value

        if self._current_page_number == self.get_total_page_count():
            self.last.disabled = True
            self.last.style = self._style.to_end_button_color_disabled.value
            self.next.disabled = True
            self.next.style = self._style.next_button_color_disabled.value
        else:
            self.last.disabled = False
            self.last.style = self._style.to_end_button_color.value
            self.next.disabled = False
            self.next.style = self._style.next_button_color.value

    @discord.ui.button(label="|<", style=discord.ButtonStyle.primary)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        await discord_utils.defer_slash_command_response(interaction=interaction)

        self._current_page_number = 1  # Always update the current page number first before updating the message

        await self.update_message()

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        await discord_utils.defer_slash_command_response(interaction=interaction)

        self._current_page_number -= 1  # Always update the current page number first before updating the message

        await self.update_message()

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await discord_utils.defer_slash_command_response(interaction=interaction)

        self._current_page_number += 1  # Always update the current page number first before updating the message

        await self.update_message()

    @discord.ui.button(label=">|", style=discord.ButtonStyle.primary)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        await discord_utils.defer_slash_command_response(interaction=interaction)

        self._current_page_number = self.get_total_page_count()  # Always update the current page number first before updating the message

        await self.update_message()


class PaginatedListViewItem:
    @property
    def name(self) -> str:
        """
        Override this method to return the name of the item.
        """
        return ""

    @property
    def value(self) -> str:
        """
        Override this method to return the value of the item.
        """
        return ""


class PaginatedListView(PaginatedView):
    def __init__(self, items: list[PaginatedListViewItem], title: str, items_per_page: int,
                 include_page_progress_in_title: bool = True,
                 starting_page_number: int = 1, style: PaginatedViewStyle = None):
        super().__init__(title=title, include_page_progress_in_title=include_page_progress_in_title,
                         starting_page_number=starting_page_number, style=style)
        self._items = items
        self._items_per_page = items_per_page

    def _get_items_for_page(self, page_number: int) -> list:
        start = (page_number - 1) * self._items_per_page
        end = start + self._items_per_page
        return self._items[start:end]

    def get_total_page_count(self) -> int:
        return len(self._items) // self._items_per_page + 1

    def render(self, page_number: int) -> discord.Embed:
        title = self._title
        if self._include_page_progress_in_title:
            title = f"{title} ({page_number}/{self._get_total_page_count()})"
        embed = discord.Embed(title=title)

        items: list[PaginatedListViewItem] = self._get_items_for_page(page_number)
        for item in items:
            embed.add_field(name=item.name, value=item.value, inline=False)

        return embed


class PaginatedCardViewItem:
    def render(self) -> discord.Embed:
        pass


class PaginatedCardView(PaginatedView):
    def __init__(self, cards: list[PaginatedCardViewItem], title: str,
                 include_page_progress_in_title: bool = True,
                 starting_page_number: int = 1, style: PaginatedViewStyle = None):
        super().__init__(title=title, include_page_progress_in_title=include_page_progress_in_title,
                         starting_page_number=starting_page_number, style=style)
        self._cards = cards

    def get_total_page_count(self) -> int:
        return len(self._cards)

    def render(self, page_number: int) -> discord.Embed:
        return self._cards[page_number - 1].render()
