import asyncio
from typing import Union, List, Tuple

import discord
from discord import Emoji
from discord.ext import commands

import modules.logs as logging
import modules.statics as statics
import modules.system_stats as system_stats
import modules.tautulli.tautulli_connector
from modules import emojis, utils
from modules.discord.command_manager import CommandManager
from modules.emojis import EmojiManager
from modules.settings.settings_transports import LibraryVoiceChannelsVisibilities
from modules.tautulli.tautulli_connector import TautulliConnector, TautulliDataResponse
from modules.utils import quote, format_thousands


async def add_emoji_reactions(message: discord.Message, count: int, emoji_manager: EmojiManager):
    """
    Add reactions to a message for user interaction
    :param message: message to add emojis to
    :param count: how many emojis to add
    :param emoji_manager: EmojiManager
    :return: None
    """

    # Only add reactions if necessary, and remove unnecessary reactions
    cache_msg = await message.channel.fetch_message(message.id)
    msg_emoji = [str(r.emoji) for r in cache_msg.reactions]

    # thanks twilsonco
    if count <= 0:
        if len(msg_emoji) > 0:
            await message.clear_reactions()
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
        elif not emoji_manager.valid_emoji_for_stream_number(emoji=e, number=i + 1):  # "6" emoji used for stream 5
            emoji_to_remove.append(e)

    # if all reactions need to be removed, do it all at once
    if len(emoji_to_remove) == len(msg_emoji):
        await message.clear_reactions()
        msg_emoji = []
    else:
        for e in emoji_to_remove:
            await message.clear_reaction(e)
            del (msg_emoji[msg_emoji.index(e)])

    for i in range(1, count + 1):
        emoji = emoji_manager.emoji_from_stream_number(i)
        if emoji not in msg_emoji:
            await message.add_reaction(emoji)


async def send_starter_message(discord_channel: discord.TextChannel) -> discord.Message:
    embed = discord.Embed(title="Welcome to Tauticord!")
    embed.add_field(name="Starting up...",
                    value='This will be replaced once we get data.',
                    inline=False)
    return await discord_channel.send(content=None, embed=embed)


async def send_message(content: TautulliDataResponse, message: discord.Message = None,
                       channel: discord.TextChannel = None):
    """
    Send or edit a message.
    :param content: Contents of the message to send
    :param message: Message to edit
    :param channel: Channel to send the message to
    :return: Message sent
    """
    # if neither channel nor message is specified, throw an error
    if not channel and not message:
        raise ValueError("Must specify either a channel or a message")
    if message:  # if message exists, use it to edit the message
        if not content.embed:  # oops, no embed to send
            await message.edit(content="Something went wrong.", embed=None)  # erase any existing content and embeds
        else:
            await message.edit(content=None, embed=content.embed)  # erase any existing content and embeds
        return message
    else:  # otherwise, send a new message in the channel
        if not content.embed:  # oops, no embed to send
            return await channel.send(content="Something went wrong.")
        else:
            return await channel.send(content=None, embed=content.embed)


async def create_discord_channel(client: discord.Client, guild_id: str, channel_name: str,
                                 channel_type: discord.ChannelType = discord.ChannelType.text,
                                 category: discord.CategoryChannel = None) -> \
        Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]:
    # guild ID is a string the whole time until here, we'll see how they account for int overflow in the future
    guild = client.get_guild(int(guild_id))  # stupid positional-only parameters
    if not guild:
        raise Exception(f"Could not load guild with ID {guild_id}")
    channel_type_string = ""
    try:
        match channel_type:
            case discord.ChannelType.voice:
                channel_type_string = "voice"
                return await guild.create_voice_channel(name=channel_name, category=category)
            case discord.ChannelType.text:
                channel_type_string = "text"
                return await guild.create_text_channel(name=channel_name, category=category)
            case discord.ChannelType.category:
                channel_type_string = "category"
                return await guild.create_category(name=channel_name)
    except:
        raise Exception(f"Could not create channel {channel_name} (type: {channel_type_string}) in guild {guild_id}")


async def get_discord_channel_by_starting_name(client: discord.Client,
                                               guild_id: str,
                                               starting_channel_name: str,
                                               channel_type: discord.ChannelType = discord.ChannelType.text,
                                               category: discord.CategoryChannel = None) -> \
        Union[discord.VoiceChannel, discord.TextChannel]:
    for channel in client.get_all_channels():
        if channel.name.startswith(starting_channel_name):
            if category and channel.category != category:
                continue
            return channel
    return await create_discord_channel(client=client,
                                        guild_id=guild_id,
                                        channel_name=starting_channel_name,
                                        channel_type=channel_type,
                                        category=category)


# TODO: create_if_not_exist is not used
async def get_discord_channel_by_name(client: discord.Client,
                                      guild_id: str,
                                      channel_name: str,
                                      channel_type: discord.ChannelType = discord.ChannelType.text,
                                      category: discord.CategoryChannel = None,
                                      create_if_not_exist: bool = True) -> \
        Union[discord.VoiceChannel, discord.TextChannel, discord.CategoryChannel, None]:
    for channel in client.get_all_channels():
        if channel.name == channel_name:
            if category and channel.category != category:
                continue
            return channel
    logging.error(f"Could not load {channel_name} channel. Attempting to create...")
    return await create_discord_channel(client=client,
                                        guild_id=guild_id,
                                        channel_name=channel_name,
                                        channel_type=channel_type,
                                        category=category)


def valid_reaction(reaction_emoji: discord.PartialEmoji,
                   reaction_user_id: int,
                   reaction_message: discord.Message,
                   reaction_type: str,
                   valid_reaction_type: str = None,
                   valid_message: discord.Message = None,
                   valid_emojis: List[str] = None,
                   valid_user_ids: List[str] = None,
                   skip_self_reaction: bool = True) -> bool:
    if skip_self_reaction and reaction_user_id == valid_message.author.id:
        return False
    if valid_reaction_type and reaction_type != valid_reaction_type:
        return False
    if valid_message and reaction_message.id != valid_message.id:
        return False
    if valid_emojis and str(reaction_emoji) not in valid_emojis:
        return False
    if valid_user_ids and str(reaction_user_id) not in valid_user_ids:
        return False
    return True


def build_response(message: discord.Message, bot_id: int, admin_ids: List[str]) -> Union[str, None]:
    # If message does not mention the bot, return None
    if bot_id not in [user.id for user in message.mentions]:
        return None

    author_id = str(message.author.id)
    if author_id == "DISCORDIDADDEDBYGITHUB":
        return "Hello, creator!"

    if author_id not in admin_ids:
        return None

    # Message mentions the bot and is from an admin
    return statics.INFO_SUMMARY


def get_voice_channel_position(stat_type: str) -> int:
    return statics.VOICE_CHANNEL_ORDER.get(stat_type, None)


class DiscordConnector:
    # noinspection PyTypeChecker
    def __init__(self,
                 token: str,
                 guild_id: str,
                 admin_ids: List[str],
                 refresh_time: int,
                 library_refresh_time: int,
                 tautulli_use_summary_message: bool,
                 tautulli_channel_name: str,
                 tautulli_connector: TautulliConnector,
                 voice_channel_settings: dict,
                 display_live_stats: bool,
                 display_library_stats: bool,
                 nitro: bool,
                 performance_monitoring: dict,
                 analytics,
                 thousands_separator: str = ""):
        self.token = token
        self.guild_id = guild_id
        self.nitro: bool = nitro
        self.admin_ids = admin_ids
        self.refresh_time = refresh_time
        self.library_refresh_time = library_refresh_time
        self.use_summary_message = tautulli_use_summary_message
        self.tautulli_channel_name = tautulli_channel_name
        self.voice_channel_settings = voice_channel_settings
        self.display_live_stats = display_live_stats
        self.display_library_stats = display_library_stats
        self.thousands_separator = thousands_separator
        self.tautulli_channel: discord.TextChannel = None
        self.tautulli_stats_voice_category: discord.CategoryChannel = None
        self.tautulli_libraries_voice_category: discord.CategoryChannel = None
        self.tautulli = tautulli_connector
        self.performance_monitoring = performance_monitoring
        self.enable_performance_monitoring = performance_monitoring.get(statics.KEY_PERFORMANCE_MONITOR_CPU,
                                                                        False) or performance_monitoring.get(
            statics.KEY_PERFORMANCE_MONITOR_MEMORY, False)
        self.performance_voice_category: discord.CategoryChannel = None
        self.analytics = analytics

        intents = discord.Intents.default()
        intents.reactions = True  # Required for on_raw_reaction_add
        intents.message_content = True  # Required for slash commands
        self.client = commands.Bot(command_prefix=statics.BOT_PREFIX,
                                   intents=intents)  # Need a Bot (subclass of Client) for cogs to work
        self.on_ready = self.client.event(self.on_ready)
        self.on_raw_reaction_add = self.client.event(self.on_raw_reaction_add)
        self.on_message = self.client.event(self.on_message)

        self.current_message = None

        self.emoji_manager: EmojiManager = EmojiManager()

        self.command_manager: CommandManager = CommandManager(
            bot=self.client,
            guild_id=self.guild_id,
            tautulli=self.tautulli,
            emoji_manager=self.emoji_manager,
            admin_ids=self.admin_ids
        )

    def connect(self) -> None:
        logging.info('Connecting to Discord...')
        # TODO: Look at merging loggers
        self.client.run(self.token, reconnect=True)

    @property
    def stats_voice_category_name(self) -> str:
        return self.voice_channel_settings.get(statics.KEY_STATS_CATEGORY_NAME, "Tautulli Stats")

    @property
    def libraries_voice_category_name(self) -> str:
        return self.voice_channel_settings.get(statics.KEY_LIBRARIES_CATEGORY_NAME, "Tautulli Libraries")

    @property
    def performance_category_name(self) -> str:
        return self.performance_monitoring.get(statics.KEY_PERFORMANCE_CATEGORY_NAME, "Performance")

    def get_voice_channel_id(self, key: str) -> int:
        return self.voice_channel_settings.get(statics.KEY_STATS_CHANNEL_IDS, {}).get(key, 0)

    async def on_ready(self) -> None:
        logging.info('Connected to Discord.')

        logging.info('Setting up Discord slash commands...')
        await self.command_manager.register_slash_commands()

        logging.info("Activating Discord slash commands...")
        await self.command_manager.activate_slash_commands()

        logging.info("Setting bot status...")
        await self.client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name='for Tautulli stats'))

        logging.info("Uploading required resources...")
        # Load normal emojis
        await self.emoji_manager.load_emojis(source_folder=statics.STANDARD_EMOJIS_FOLDER, client=self.client,
                                             guild_id=self.guild_id)
        # Load extra emojis if Nitro is enabled
        if self.nitro:
            await self.emoji_manager.load_emojis(source_folder=statics.NITRO_EMOJIS_FOLDER, client=self.client,
                                                 guild_id=self.guild_id)

        if self.use_summary_message:
            logging.info("Loading Tautulli text settings...")
            await self.collect_discord_text_channel()
            await self.collect_old_message_in_tautulli_channel()

        logging.info("Loading Tautulli voice settings...")
        # Only grab the voice category (make it) if we're going to use it
        if self.display_live_stats:
            # only grab the stats voice category (make it) if stats channel IDs are not manually set
            if not self.voice_channel_settings.get(statics.KEY_USE_STATS_CHANNEL_IDS, False):
                self.tautulli_stats_voice_category = await self.collect_discord_voice_category(
                    category_name=self.stats_voice_category_name)
        if self.display_library_stats:
            self.tautulli_libraries_voice_category = await self.collect_discord_voice_category(
                category_name=self.libraries_voice_category_name)
        if self.enable_performance_monitoring:
            self.performance_voice_category = await self.collect_discord_voice_category(
                category_name=self.performance_category_name)

        logging.info("Loading Tautulli summary service...")
        # minimum 5-second sleep time hard-coded, trust me, don't DDoS your server
        # noinspection PyAsyncCall
        asyncio.create_task(self.run_live_summary_service(message=self.current_message,
                                                          refresh_time=max([5, self.refresh_time])))

        logging.info("Starting Tautulli library stats service...")
        # minimum 5-minute sleep time hard-coded, trust me, don't DDoS your server
        # noinspection PyAsyncCall
        asyncio.create_task(self.run_library_stats_service(refresh_time=max([5 * 60, self.library_refresh_time])))

        if self.enable_performance_monitoring:
            logging.info("Starting performance monitoring service...")
            # noinspection PyAsyncCall
            asyncio.create_task(
                self.run_performance_monitoring_service(refresh_time=5 * 60))  # Hard-coded 5-minute refresh time

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        emoji = payload.emoji
        user_id = payload.user_id
        message = await self.tautulli_channel.fetch_message(payload.message_id)
        reaction_type = "REACTION_ADD"

        if valid_reaction(reaction_emoji=emoji,
                          reaction_user_id=user_id,
                          reaction_message=message,
                          reaction_type=reaction_type,
                          valid_message=self.current_message,
                          valid_reaction_type=None,  # We already know it's the right type
                          valid_emojis=self.emoji_manager.stream_number_emojis,
                          valid_user_ids=self.admin_ids):
            # message here will be the current message, so we can just use that
            end_notification = await self.stop_tautulli_stream_via_reaction_emoji(emoji=emoji, message=message)
            if end_notification:
                await end_notification.delete(delay=5)  # delete after 5 seconds

    async def on_message(self, message: discord.Message) -> None:
        response = build_response(message=message, bot_id=self.client.user.id, admin_ids=self.admin_ids)

        if response:
            await message.channel.send(response)

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

    async def run_live_summary_service(self, message: discord.Message, refresh_time: int):
        while True:
            try:
                message = await self.edit_summary_data(previous_message=message)
                await asyncio.sleep(refresh_time)
            except Exception:
                exit(1)  # Die on any unhandled exception for this subprocess (i.e. internet connection loss)

    async def run_library_stats_service(self, refresh_time: int):
        if not self.tautulli_libraries_voice_category:
            return  # No libraries voice category set, so don't bother
        while True:
            try:
                await self.update_library_stats_voice_channels()
                await asyncio.sleep(refresh_time)
            except Exception:
                exit(1)  # Die on any unhandled exception for this subprocess (i.e. internet connection loss)

    async def run_performance_monitoring_service(self, refresh_time: int):
        if not self.performance_voice_category:
            return  # No performance voice category set, so don't bother
        while True:
            try:
                await self.update_performance_voice_channels()
                await asyncio.sleep(refresh_time)
            except Exception:
                exit(1)  # Die on any unhandled exception for this subprocess (i.e. internet connection loss)

    def is_me(self, message) -> bool:
        return message.author == self.client.user

    async def stop_tautulli_stream_via_reaction_emoji(self, emoji: discord.PartialEmoji, message: discord.Message) -> \
            discord.Message:
        stream_number: int = self.emoji_manager.stream_number_from_emoji(emoji=emoji)

        logging.debug(f"Stopping stream {emoji}...")
        stopped_message = self.tautulli.stop_stream(emoji=emoji, stream_number=stream_number)
        logging.info(stopped_message)
        end_notification = await self.tautulli_channel.send(content=stopped_message)
        await message.clear_reaction(str(emoji))
        return end_notification

    async def edit_summary_data(self, previous_message) -> discord.Message:
        """
        Collect new summary info, replace old message with new one (if enabled), update stats voice channels (if enabled)
        :param previous_message: discord.Message to replace
        :return: new discord.Message
        """
        data_wrapper, count, activity, plex_online = self.tautulli.refresh_data(emoji_manager=self.emoji_manager)

        await self.update_live_voice_channels(activity=activity,
                                              plex_online=plex_online,
                                              category=self.tautulli_stats_voice_category)

        # Skip updating the summary message if the setting is disabled
        if not self.use_summary_message:
            return self.current_message

        """
        For performance and aesthetics, edit the old message if:
        1) the old message is the newest message in the channel, or
        2) if the only messages that are newer were written by this bot 
        (which would be stream stop messages that have already been deleted)
        """
        use_old_message = False
        async for msg in self.tautulli_channel.history(limit=100):
            if msg.author != self.client.user:
                use_old_message = False
                break
            elif msg.id == previous_message.id:
                use_old_message = True
                break

        if use_old_message:
            # reuse the old message to avoid spamming the channel
            logging.debug('Using old message...')
            await previous_message.clear_reactions()
            if not activity or data_wrapper.error:
                # error when refreshing Tautulli data, new_message is string (i.e. "Connection lost")
                logging.debug("Editing old message with Tautulli error...")
            else:
                logging.debug('Editing old message...')
            # update the message regardless of whether the content has changed
            new_message = await send_message(content=data_wrapper,
                                             message=previous_message)
        else:
            # send a new message each time
            # first, attempt to delete the start-up message if it exists
            try:
                await previous_message.delete()
            except Exception as delete_exception:
                logging.debug(f"Failed to delete old (specified) message: {delete_exception}")
                await self.tautulli_channel.purge(check=self.is_me)
            # send new message
            logging.debug("Using new message...")
            if not activity or data_wrapper.error:
                # error when refreshing Tautulli data, new_message is string (i.e. "Connection lost")
                logging.debug("Sending new message with Tautulli error...")
            else:
                logging.debug('Sending new message...')
            # send a new message, regardless of whether the content has changed
            new_message = await send_message(content=data_wrapper, channel=self.tautulli_channel)

        if data_wrapper.plex_pass:
            await add_emoji_reactions(message=new_message, count=count, emoji_manager=self.emoji_manager)
            # on_raw_reaction_add will handle the rest

        # Store the message
        self.current_message = new_message
        return self.current_message

    async def collect_discord_text_channel(self) -> None:
        logging.info(f"Getting {quote(self.tautulli_channel_name)} channel")
        self.tautulli_channel: discord.TextChannel = \
            await get_discord_channel_by_name(client=self.client,
                                              guild_id=self.guild_id,
                                              channel_name=self.tautulli_channel_name)
        if not self.tautulli_channel:
            raise Exception(f"Could not load {quote(self.tautulli_channel_name)} channel. Exiting...")
        logging.info(f"{quote(self.tautulli_channel_name)} channel collected.")

    async def collect_discord_voice_category(self,
                                             category_name: str,
                                             create_if_not_exist: bool = False) -> discord.CategoryChannel:
        logging.info(f"Getting {quote(category_name)} voice category")
        category: discord.CategoryChannel = \
            await get_discord_channel_by_name(client=self.client,
                                              guild_id=self.guild_id,
                                              channel_name=category_name,
                                              channel_type=discord.ChannelType.category,
                                              create_if_not_exist=create_if_not_exist)
        if not category_name:
            raise Exception(f"Could not load {quote(category_name)} voice category. Exiting...")
        logging.info(f"{quote(category_name)} voice category collected.")
        return category

    async def collect_old_message_in_tautulli_channel(self) -> None:
        """
        Get the last message sent in the Tautulli channel, used to start the bot loop
        :return: discord.Message
        """
        # If the very last message in the channel is from Tauticord, use it
        async for msg in self.tautulli_channel.history(limit=1):
            if msg.author == self.client.user:
                await msg.clear_reactions()

                # Store the message
                self.current_message = msg
                return

        # If the very last message in the channel is not from Tauticord, make a new one.
        logging.info("Couldn't find old message, sending initial message...")
        starter_message = await send_starter_message(discord_channel=self.tautulli_channel)
        # Store the message
        self.current_message = starter_message
        return

    async def edit_stat_voice_channel_by_name(self,
                                              stat: Union[int, float, str],
                                              channel_name: str = None,
                                              category: discord.CategoryChannel = None) -> None:
        channel = await get_discord_channel_by_starting_name(client=self.client,
                                                             guild_id=self.guild_id,
                                                             starting_channel_name=f"{channel_name}:",
                                                             channel_type=discord.ChannelType.voice,
                                                             category=category)
        if not channel:
            logging.error(f"Could not load {channel_name} channel")
        else:
            try:
                await channel.edit(name=f"{channel_name}: {stat}",
                                   category=category)
            except Exception as voice_channel_edit_error:
                logging.error(f"Error editing {channel_name} voice channel: {voice_channel_edit_error}")

    async def edit_stat_voice_channel_by_id(self,
                                            stat: Union[int, float, str],
                                            channel_name: str,
                                            channel_id: int):
        channel = await self.client.fetch_channel(channel_id)
        if not channel:
            logging.error(f"Could not load channel with ID {channel_id}")
        else:
            try:
                await channel.edit(name=f"{channel_name}: {stat}")
            except Exception as voice_channel_edit_error:
                logging.error(f"Error editing {channel_name} voice channel: {voice_channel_edit_error}")

    async def edit_stat_voice_channel(self,
                                      channel_name: str,
                                      stat: Union[int, float, str],
                                      channel_id: int = 0,
                                      category: discord.CategoryChannel = None) -> None:
        # NOTE: category can be None if user is providing Channel IDs manually
        if channel_id != 0:
            await self.edit_stat_voice_channel_by_id(stat=stat, channel_name=channel_name, channel_id=channel_id)
        else:
            await self.edit_stat_voice_channel_by_name(stat=stat, channel_name=channel_name, category=category)

    async def update_live_voice_channels(self,
                                         activity: modules.tautulli.tautulli_connector.Activity,
                                         plex_online: bool,
                                         category: discord.CategoryChannel = None) -> None:

        if self.voice_channel_settings.get(statics.KEY_PLEX_STATUS, False):
            status = "Online" if plex_online else "Offline"
            logging.info(f"Updating Plex Status voice channel with new status: {status}")
            if self.voice_channel_settings.get(statics.KEY_PLEX_STATUS_USE_EMOJI, False):
                status = self.emoji_manager.get_emoji(key=f'plex_{status.lower()}')
            await self.edit_stat_voice_channel(channel_name="Plex Status",
                                               channel_id=self.get_voice_channel_id(
                                                   key=statics.KEY_PLEX_STATUS_CHANNEL_ID),
                                               stat=status,
                                               category=category)

        if activity:
            if self.voice_channel_settings.get(statics.KEY_COUNT, False):
                count = activity.stream_count
                logging.info(f"Updating Streams voice channel with new stream count: {count}")
                await self.edit_stat_voice_channel(channel_name="Current Streams",
                                                   channel_id=self.get_voice_channel_id(
                                                       key=statics.KEY_STREAM_COUNT_CHANNEL_ID),
                                                   stat=count,
                                                   category=category)
            if self.voice_channel_settings.get(statics.KEY_TRANSCODE_COUNT, False):
                count = activity.transcode_count
                logging.info(f"Updating Transcodes voice channel with new stream count: {count}")
                await self.edit_stat_voice_channel(channel_name="Current Transcodes",
                                                   channel_id=self.get_voice_channel_id(
                                                       key=statics.KEY_TRANSCODE_COUNT_CHANNEL_ID),
                                                   stat=count,
                                                   category=category)
            if self.voice_channel_settings.get(statics.KEY_BANDWIDTH, False):
                bandwidth = activity.total_bandwidth
                logging.info(f"Updating Bandwidth voice channel with new bandwidth: {bandwidth}")
                await self.edit_stat_voice_channel(channel_name="Bandwidth",
                                                   channel_id=self.get_voice_channel_id(
                                                       key=statics.KEY_BANDWIDTH_CHANNEL_ID),
                                                   stat=bandwidth,
                                                   category=category)
            if self.voice_channel_settings.get(statics.KEY_LAN_BANDWIDTH, False):
                bandwidth = activity.lan_bandwidth
                logging.info(f"Updating Local Bandwidth voice channel with new bandwidth: {bandwidth}")
                await self.edit_stat_voice_channel(channel_name="Local BW",
                                                   channel_id=self.get_voice_channel_id(
                                                       key=statics.KEY_LAN_BANDWIDTH_CHANNEL_ID),
                                                   stat=bandwidth,
                                                   category=category)
            if self.voice_channel_settings.get(statics.KEY_REMOTE_BANDWIDTH, False):
                bandwidth = activity.wan_bandwidth
                logging.info(f"Updating Remote Bandwidth voice channel with new bandwidth: {bandwidth}")
                await self.edit_stat_voice_channel(channel_name="Remote BW",
                                                   channel_id=self.get_voice_channel_id(
                                                       key=statics.KEY_REMOTE_BANDWIDTH_CHANNEL_ID),
                                                   stat=bandwidth,
                                                   category=category)

    async def get_library_stats(self) -> List[Tuple[str, List[Tuple[str, int]]]]:
        all_stats = []
        visibility_settings = LibraryVoiceChannelsVisibilities(settings=self.voice_channel_settings)

        for library_name in self.voice_channel_settings.get(statics.KEY_LIBRARIES, []):
            stats: List[Tuple[str, int]] = self.tautulli.get_library_item_count(library_name=library_name,
                                                                                emoji_manager=self.emoji_manager,
                                                                                visibility_settings=visibility_settings)
            if not stats:
                continue
            all_stats.append((library_name, stats))

        for encoded_value in self.voice_channel_settings.get(statics.KEY_COMBINED_LIBRARIES, []):
            voice_channel_name, library_names = utils.decode_combined_tautulli_libraries(
                encoded_string=encoded_value)
            stats: [List[Tuple[str, int]]] = self.tautulli.get_combined_library_item_count(
                library_names=library_names,
                emoji_manager=self.emoji_manager,
                visibility_settings=visibility_settings)
            if not stats:
                continue
            all_stats.append((voice_channel_name, stats))

        return all_stats

    async def update_library_stats_voice_channels(self) -> None:
        logging.info("Updating library stats...")
        if self.voice_channel_settings.get(statics.KEY_STATS, False):
            all_stats = await self.get_library_stats()
            for entry in all_stats:
                library_name = entry[0]
                stats = entry[1]
                for stat in stats:
                    stat_emoji = stat[0] if self.voice_channel_settings.get(statics.KEY_USE_EMOJIS, True) else None
                    stat_value = stat[1]
                    stat_value = format_thousands(number=stat_value, delimiter=self.thousands_separator)
                    channel_name = f"{library_name}"
                    if stat_emoji:
                        channel_name = f"{stat_emoji} {channel_name}"
                    logging.info(f"Updating {library_name} voice channel with new library size: {stat_value}")
                    await self.edit_stat_voice_channel(channel_name=channel_name,
                                                       stat=stat_value,
                                                       category=self.tautulli_libraries_voice_category)

    async def update_performance_voice_channels(self) -> None:
        logging.info("Updating performance stats...")
        if self.performance_monitoring.get(statics.KEY_PERFORMANCE_MONITOR_TAUTULLI_USER_COUNT, False):
            user_count = self.tautulli.get_user_count()
            logging.info(f"Updating Users voice channel with new user count: {user_count}")
            await self.edit_stat_voice_channel(channel_name="Users",
                                               stat=user_count,
                                               category=self.performance_voice_category)
        if self.performance_monitoring.get(statics.KEY_PERFORMANCE_MONITOR_DISK_SPACE, False):
            path = self.performance_monitoring.get(statics.KEY_PERFORMANCE_MONITOR_DISK_SPACE_PATH,
                                                   statics.MONITORED_DISK_SPACE_FOLDER)
            if not system_stats.path_exists(path):
                logging.error(f"Could not find {quote(path)} to monitor disk space.")
                stat = "N/A"
            else:
                stat = system_stats.disk_usage_display(path)
            logging.info(f"Updating Disk voice channel with new disk space: {stat}")
            await self.edit_stat_voice_channel(channel_name="Disk",
                                               stat=stat,
                                               category=self.performance_voice_category)
        if self.performance_monitoring.get(statics.KEY_PERFORMANCE_MONITOR_CPU, False):
            cpu_percent = f"{utils.format_decimal(system_stats.cpu_usage())}%"
            logging.info(f"Updating CPU voice channel with new CPU percent: {cpu_percent}")
            await self.edit_stat_voice_channel(channel_name="CPU",
                                               stat=cpu_percent,
                                               category=self.performance_voice_category)

        if self.performance_monitoring.get(statics.KEY_PERFORMANCE_MONITOR_MEMORY, False):
            memory_percent = f"{utils.format_decimal(system_stats.ram_usage())} GB ({utils.format_decimal(system_stats.ram_usage_percentage())}%)"
            logging.info(f"Updating Memory voice channel with new Memory percent: {memory_percent}")
            await self.edit_stat_voice_channel(channel_name="Memory",
                                               stat=memory_percent,
                                               category=self.performance_voice_category)
