import discord
from discord.ext import commands

import modules.logs as logging
import modules.settings.models as settings_models
import modules.statics as statics
from modules.discord import discord_utils
from modules.discord.services.base_service import BaseService
from modules.emojis import EmojiManager


class Bot:
    def __init__(self,
                 bot_token: str,
                 services: list[BaseService],
                 discord_status_settings: settings_models.DiscordStatusMessage,
                 guild_id: int,
                 emoji_manager: EmojiManager):
        self._token = bot_token
        self._services = services
        self.discord_status_settings = discord_status_settings
        self.guild_id = guild_id
        self.emoji_manager = emoji_manager

        intents = discord.Intents.default()
        intents.reactions = True  # Required for on_raw_reaction_add
        intents.message_content = True  # Required for slash commands
        self.client = commands.Bot(command_prefix=statics.BOT_PREFIX,
                                   intents=intents)  # Need a Bot (subclass of Client) for cogs to work

        self.on_ready = self.client.event(self.on_ready)

    def connect(self) -> None:
        # TODO: Look at merging loggers
        self.client.run(self._token, reconnect=True)  # Can't have any asyncio tasks running before the bot is ready

    async def on_ready(self):
        # Set bot status if required
        if self.discord_status_settings.should_update_on_startup:
            logging.info("Setting bot status...")
            activity_name = self.discord_status_settings.activity_name
            message = self.discord_status_settings.message(
                stream_count=0,  # No streams on startup, use fallback
                fallback="Starting up...")
            await discord_utils.update_presence(client=self.client,
                                                activity_name=activity_name,
                                                line_one=message)

        logging.info("Uploading required resources...")

        # How many emoji slots are left (excluding any emojis that have already been uploaded; avoid re-uploading)
        available_emoji_slots = await discord_utils.available_emoji_slots(client=self.client, guild_id=self.guild_id)
        un_uploaded_emoji_count = len(await self.emoji_manager.get_un_uploaded_emoji_files(
            client=self.client, guild_id=self.guild_id))

        if un_uploaded_emoji_count > 0:
            if available_emoji_slots < un_uploaded_emoji_count:
                logging.fatal(
                    f"Insufficient emoji slots to upload {un_uploaded_emoji_count} custom emojis, will use built-in emojis instead.")
            else:
                await self.emoji_manager.load_custom_emojis(client=self.client, guild_id=self.guild_id)
                available_emoji_slots -= un_uploaded_emoji_count

        print('Bot is ready.')

        # Activate services
        for service in self._services:
            await service.register_bot(bot=self.client)
            await service.associate_bot_callbacks()
            if await service.enabled():
                await service.on_ready()
