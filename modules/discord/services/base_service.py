import discord
from discord.ext import commands

import modules.logs as logging
from modules.discord import discord_utils
from modules.utils import quote


class BaseService:
    """
    Base class for a service aspect of the Discord bot. These start running when the bot is ready (connected to Discord).
    """

    def __init__(self):
        self.bot: commands.Bot = None  # type: ignore

    async def register_bot(self, bot: commands.Bot):
        """
        Register the bot with the service.
        `self.bot` will not be set until this is called.
        """
        self.bot = bot

    async def associate_bot_callbacks(self):
        """
        Associate bot callbacks with the service.
        `self.bot` will be set when this is called.
        This is where you should register your bot callbacks (`on_raw_reaction_add`, etc.).
        """
        pass

    async def on_ready(self):
        """
        Called when the bot is ready. This is where you should start your service.
        `self.bot` will be set when this is called.
        """
        raise NotImplementedError

    async def enabled(self) -> bool:
        """
        Return whether the service is enabled.
        Will run `on_ready` only if this returns True.
        `self.bot` will be set when this is called.
        """
        raise NotImplementedError

    async def collect_discord_voice_category(self,
                                             guild_id: int,
                                             category_name: str) -> discord.CategoryChannel:
        assert self.bot, "Bot not registered. Exiting..."

        logging.debug(f"Getting {quote(category_name)} voice category")

        category = await discord_utils.get_or_create_discord_category_by_name(client=self.bot,
                                                                              guild_id=guild_id,
                                                                              category_name=category_name)

        if not category:
            raise Exception(f"Could not load {quote(category_name)} voice category. Exiting...")

        logging.debug(f"{quote(category_name)} voice category collected.")
        return category

    async def collect_discord_text_channel(self,
                                           guild_id: int,
                                           channel_name: str) -> discord.TextChannel:
        assert self.bot, "Bot not registered. Exiting..."

        logging.debug(f"Getting {quote(channel_name)} text channel")

        channel = await discord_utils.get_or_create_discord_channel_by_name(client=self.bot,
                                                                            guild_id=guild_id,
                                                                            channel_name=channel_name,
                                                                            channel_type=discord.ChannelType.text)

        if not channel:
            raise Exception(f"Could not load {quote(channel_name)} text channel. Exiting...")

        logging.debug(f"{quote(channel_name)} text channel collected.")
        return channel

    async def collect_discord_voice_channel(self,
                                            guild_id: int,
                                            channel_name: str) -> discord.VoiceChannel:
        assert self.bot, "Bot not registered. Exiting..."

        logging.debug(f"Getting {quote(channel_name)} voice channel")

        channel = await discord_utils.get_or_create_discord_channel_by_name(client=self.bot,
                                                                            guild_id=guild_id,
                                                                            channel_name=channel_name,
                                                                            channel_type=discord.ChannelType.voice)

        if not channel:
            raise Exception(f"Could not load {quote(channel_name)} voice channel. Exiting...")

        logging.debug(f"{quote(channel_name)} voice channel collected.")
        return channel
