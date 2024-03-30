import asyncio
from typing import Union

import discord
from discord import Emoji
from discord.ext import commands

import modules.logs as logging
import modules.settings.models as settings_models
import modules.statics as statics
import modules.tautulli.tautulli_connector
from modules import versioning
from modules.analytics import GoogleAnalytics
from modules.discord import discord_utils
from modules.discord.command_manager import CommandManager
from modules.emojis import EmojiManager
from modules.tasks.activity import ActivityStatsAndSummaryMessage
from modules.tasks.library_stats import LibraryStats
from modules.tasks.message_handler import MessageHandler
from modules.tasks.performance_stats import PerformanceMonitor
from modules.utils import quote


class DiscordConnector:
    # noinspection PyTypeChecker
    def __init__(self,
                 tautulli_connector: modules.tautulli.tautulli_connector.TautulliConnector,
                 discord_settings: settings_models.Discord,
                 tautulli_settings: settings_models.Tautulli,
                 display_settings: settings_models.Display,
                 run_args_settings: settings_models.RunArgs,
                 stats_settings: settings_models.Stats,
                 analytics: GoogleAnalytics,
                 version_checker: versioning.VersionChecker):
        self.tautulli: modules.tautulli.tautulli_connector.TautulliConnector = tautulli_connector
        self.token: str = discord_settings.bot_token
        self.guild_id: int = discord_settings.server_id
        self.admin_ids: list[int] = discord_settings.admin_ids
        self.refresh_time: int = tautulli_settings.refresh_interval_seconds
        self.library_refresh_time: int = stats_settings.library.refresh_interval_seconds
        self.use_summary_message: bool = discord_settings.use_summary_message
        self.stats_settings: settings_models.Stats = stats_settings
        self.run_args_settings: settings_models.RunArgs = run_args_settings
        self.thousands_separator: str = display_settings.thousands_separator
        self.analytics: GoogleAnalytics = analytics

        self.tautulli_summary_channel_name: str = discord_settings.channel_name
        self.tautulli_summary_channel: discord.TextChannel = None

        self.activity_monitor: ActivityStatsAndSummaryMessage = None
        self.library_stats_monitor: LibraryStats = None
        self.performance_stats_monitor: PerformanceMonitor = None

        intents = discord.Intents.default()
        intents.reactions = True  # Required for on_raw_reaction_add
        intents.message_content = True  # Required for slash commands
        self.client = commands.Bot(command_prefix=statics.BOT_PREFIX,
                                   intents=intents)  # Need a Bot (subclass of Client) for cogs to work

        self.on_ready = self.client.event(self.on_ready)
        self.on_raw_reaction_add = self.client.event(self.on_raw_reaction_add)
        self.message_handler = MessageHandler(client=self.client, admin_ids=self.admin_ids)
        self.on_message = self.client.event(self.message_handler.on_message)

        self.emoji_manager: EmojiManager = EmojiManager()

        self.command_manager: CommandManager = CommandManager(
            enable_slash_commands=discord_settings.enable_slash_commands,
            bot=self.client,
            guild_id=self.guild_id,
            tautulli=self.tautulli,
            emoji_manager=self.emoji_manager,
            admin_ids=self.admin_ids,
        )

        self.version_checker = version_checker

    def connect(self) -> None:
        logging.info('Connecting to Discord...')
        # TODO: Look at merging loggers
        self.client.run(self.token, reconnect=True)  # Can't have any asyncio tasks running before the bot is ready

    async def on_ready(self) -> None:
        # NOTE: This is the first place in the stack where asyncio tasks can be started

        logging.info('Connected to Discord.')

        logging.info('Setting up Discord slash commands...')

        await self.command_manager.register_slash_commands()

        logging.info("Setting bot status...")

        await self.client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name='for Tautulli stats'))

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

        logging.info("Loading Tautulli summary service...")

        summary_message = None
        if self.use_summary_message:
            logging.info("Loading Tautulli text channel settings...")

            self.tautulli_summary_channel: discord.TextChannel = \
                await discord_utils.get_or_create_discord_channel_by_name(
                    client=self.client,
                    guild_id=self.guild_id,
                    channel_name=self.tautulli_summary_channel_name)
            if not self.tautulli_summary_channel:
                raise Exception(f"Could not load {quote(self.tautulli_summary_channel_name)} channel. Exiting...")

            logging.info(f"{quote(self.tautulli_summary_channel_name)} channel collected.")

            # If the very last message in the channel is from Tauticord, use it
            async for msg in self.tautulli_summary_channel.history(limit=1):
                if msg.author == self.client.user:
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

        activity_stats_voice_category = None
        if self.stats_settings.activity.enable:
            logging.info("Loading Tautulli activity stats settings...")
            activity_stats_voice_category = await self.collect_discord_voice_category(
                category_name=self.stats_settings.activity.category_name)

        # minimum 5-second sleep time hard-coded, trust me, don't DDoS your server
        refresh_time = max([5, self.refresh_time])
        # This handles both text channel updates AND activity stats voice channel updates
        self.activity_monitor = ActivityStatsAndSummaryMessage(discord_client=self.client,
                                                               settings=self.stats_settings.activity,
                                                               tautulli_connector=self.tautulli,
                                                               guild_id=self.guild_id,
                                                               message=summary_message,
                                                               emoji_manager=self.emoji_manager,
                                                               version_checker=self.version_checker,
                                                               voice_category=activity_stats_voice_category)
        # noinspection PyAsyncCall
        asyncio.create_task(self.activity_monitor.run_service(interval_seconds=refresh_time))

        logging.info("Loading additional Tautulli voice settings...")

        if self.stats_settings.library.enable:
            logging.info("Starting Tautulli library stats service...")
            voice_category = await self.collect_discord_voice_category(
                category_name=self.stats_settings.library.category_name)
            # minimum 5-minute sleep time hard-coded, trust me, don't DDoS your server
            refresh_time = max([5 * 60,
                                self.library_refresh_time])
            self.library_stats_monitor = LibraryStats(discord_client=self.client,
                                                      settings=self.stats_settings.library,
                                                      tautulli_connector=self.tautulli,
                                                      guild_id=self.guild_id,
                                                      voice_category=voice_category)
            # noinspection PyAsyncCall
            asyncio.create_task(self.library_stats_monitor.run_service(interval_seconds=refresh_time))

        if self.stats_settings.performance.enable:
            logging.info("Starting performance monitoring service...")
            voice_category = await self.collect_discord_voice_category(
                category_name=self.stats_settings.performance.category_name)
            # Hard-coded 5-minute refresh time
            refresh_time = 5 * 60
            self.performance_stats_monitor = PerformanceMonitor(discord_client=self.client,
                                                                settings=self.stats_settings.performance,
                                                                tautulli_connector=self.tautulli,
                                                                run_args_settings=self.run_args_settings,
                                                                guild_id=self.guild_id,
                                                                voice_category=voice_category)
            # noinspection PyAsyncCall
            asyncio.create_task(self.performance_stats_monitor.run_service(interval_seconds=refresh_time))

        if self.version_checker and self.version_checker.enable:
            logging.info("Starting version checking service...")
            # noinspection PyAsyncCall
            asyncio.create_task(self.version_checker.check_for_new_version())

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

    async def collect_guild_emojis(self) -> tuple[Emoji, ...]:
        # guild ID is a string the whole time until here, we'll see how they account for int overflow in the future
        guild = self.client.get_guild(int(self.guild_id))  # stupid positional-only parameters
        return guild.emojis

    async def upload_new_emoji(self, file: str, name: str) -> Union[discord.Emoji, None]:
        """
        Upload a new emoji to the server
        :param file: Path to the file to upload
        :param name: Name of the emoji
        :return: None
        """
        # guild ID is a string the whole time until here, we'll see how they account for int overflow in the future
        guild = self.client.get_guild(int(self.guild_id))  # stupid positional-only parameters

        # Check if the emoji already exists
        for emoji in guild.emojis:
            if emoji.name == name:
                return emoji

        # Upload the new emoji
        try:
            with open(file, 'rb') as f:
                image_bytes: bytes = f.read()
                return await guild.create_custom_emoji(name=name, image=image_bytes, reason="Tauticord emoji upload")
        except Exception as e:
            logging.error(f"Failed to upload emoji {name} to server: {e}. Will use default emoji instead.")
            return None

    def is_me(self, message) -> bool:
        return message.author == self.client.user

    async def stop_tautulli_stream_via_reaction_emoji(self, emoji: discord.PartialEmoji, message: discord.Message) -> \
            discord.Message:
        stream_number: int = self.emoji_manager.stream_number_from_emoji(emoji=emoji)

        logging.debug(f"Stopping stream {emoji}...")
        stopped_message = self.tautulli.stop_stream(emoji=emoji, stream_number=stream_number)
        logging.info(stopped_message)
        end_notification = await self.tautulli_summary_channel.send(content=stopped_message)
        await message.clear_reaction(str(emoji))
        return end_notification

    async def collect_discord_voice_category(self,
                                             category_name: str) -> discord.CategoryChannel:
        logging.info(f"Getting {quote(category_name)} voice category")
        category = await discord_utils.get_or_create_discord_category_by_name(client=self.client,
                                                                              guild_id=self.guild_id,
                                                                              category_name=category_name)

        if not category:
            raise Exception(f"Could not load {quote(category_name)} voice category. Exiting...")

        logging.info(f"{quote(category_name)} voice category collected.")
        return category
