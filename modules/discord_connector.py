import asyncio
import sys
from typing import Union

import discord
from discord.ext import tasks

import modules.statics as statics
from modules.logs import info, debug, error
from modules.tautulli_connector import TautulliConnector, TautulliDataResponse


async def start_bot(discord_connector, analytics):
    """
    Start the bot cycle
    :param analytics: GoogleAnalytics object
    :param discord_connector: DiscordConnector object
    :return: None
    """
    info("Starting monitoring...")
    analytics.event(event_category="Platform", event_action=sys.platform)
    await discord_connector.get_tautulli_channel()
    message = await discord_connector.get_old_message_in_tautulli_channel()
    while True:
        message = await discord_connector.edit_message(previous_message=message)


async def add_emoji_number_reactions(message: discord.Message, count: int):
    """
    Add number reactions to a message for user interaction
    :param message: message to add emojis to
    :param count: how many emojis to add
    :return: None
    """

    if count <= 0:
        return

    # Only add reactions if necessary, and remove unnecessary reactions
    cache_msg = await message.channel.fetch_message(message.id)
    msg_emoji = [str(r.emoji) for r in cache_msg.reactions]

    # thanks twilsonco
    if count <= 0:
        if len(msg_emoji) > 0:
            await message.clear_reactions()
        return

    emoji_to_remove = []

    for i, e in enumerate(msg_emoji):
        if i >= count or i != statics.emoji_numbers.index(e):
            emoji_to_remove.append(e)

    # if all reactions need to be removed, do it all at once
    if len(emoji_to_remove) == len(msg_emoji):
        await message.clear_reactions()
        msg_emoji = []
    else:
        for e in emoji_to_remove:
            await message.clear_reaction(e)
            del (msg_emoji[msg_emoji.index(e)])

    for i in range(0, count):
        if statics.emoji_numbers[i] not in msg_emoji:
            await message.add_reaction(statics.emoji_numbers[i])


async def send_starter_message(tautulli_connector, discord_channel: discord.TextChannel) -> discord.Message:
    if tautulli_connector.use_embeds:
        embed = discord.Embed(title="Welcome to Tauticord!")
        embed.add_field(name="Starting up...",
                        value='This will be replaced once we get data.',
                        inline=False)
        return await discord_channel.send(content=None, embed=embed)
    else:
        return await discord_channel.send(content="Welcome to Tauticord!")


async def send_message(content: TautulliDataResponse, embed: bool = False, message: discord.Message = None,
                       channel: discord.TextChannel = None):
    """
    Send or edit a message.
    :param content: Contents of the message to send
    :param embed: Whether to use embeds
    :param message: Message to edit
    :param channel: Channel to send the message to
    :return: Message sent
    """
    # if neither channel nor message is specified, throw an error
    if not channel and not message:
        raise ValueError("Must specify either a channel or a message")
    if message:  # if message exists, use it to edit the message
        if embed:  # let's send an embed
            if not content.embed:  # oops, no embed to send
                await message.edit(content="Something went wrong.", embed=None)  # erase any existing content and embeds
            else:
                await message.edit(content=None, embed=content.embed)  # erase any existing content and embeds
        else:  # let's send a normal message
            if not content.message:  # oops, no message to send
                await message.edit(content="Something went wrong.", embed=None)  # erase any existing content and embeds
            else:
                await message.edit(content=content.message, embed=None)  # erase any existing content and embeds
        return message
    else:  # otherwise, send a new message in the channel
        if embed:  # let's send an embed
            if not content.embed:  # oops, no embed to send
                return await channel.send(content="Something went wrong.")
            else:
                return await channel.send(content=None, embed=content.embed)
        else:  # let's send a normal message
            if not content.message:  # oops, no message to send
                return await channel.send(content="Something went wrong.")
            else:
                return await channel.send(content=content.message)


class DiscordConnector:
    def __init__(self,
                 token: str,
                 guild_id: int,
                 owner_id: int,
                 refresh_time: int,
                 tautulli_channel_name: str,
                 tautulli_connector: TautulliConnector,
                 analytics,
                 use_embeds: bool):
        self.token = token
        self.guild_id = guild_id
        self.owner_id = owner_id
        self._refresh_time = refresh_time
        self.tautulli_channel_name = tautulli_channel_name
        self.tautulli_channel: discord.TextChannel = None
        self.tautulli = tautulli_connector
        self.analytics = analytics
        self.use_embeds = use_embeds
        self.client = discord.Client(intents=discord.Intents.default())
        self.on_ready = self.client.event(self.on_ready)

    @property
    def refresh_time(self) -> int:
        return max([5, self._refresh_time])  # minimum 5-second sleep time hard-coded, trust me, don't DDoS your server

    async def on_ready(self) -> None:
        info('Connected to Discord.')
        self.update_libraries.start()
        await start_bot(discord_connector=self, analytics=self.analytics)

    def connect(self) -> None:
        info('Connecting to Discord...')
        self.client.run(self.token)

    def is_me(self, message) -> bool:
        return message.author == self.client.user

    async def edit_message(self, previous_message) -> discord.Message:
        """
        Collect new summary info, replace old message with new one
        :param previous_message: discord.Message to replace
        :return: new discord.Message
        """
        data_wrapper, count, activity = self.tautulli.refresh_data()

        await self.update_voice_channels(activity)

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
            debug('Using old message...')
            if not activity or data_wrapper.error:
                # error when refreshing Tautulli data, new_message is string (i.e. "Connection lost")
                debug("Editing old message with Tautulli error...")
            else:
                debug('Editing old message...')
            # update the message regardless of whether the content has changed
            new_message = await send_message(content=data_wrapper,
                                             embed=self.use_embeds,
                                             message=previous_message)
        else:
            # send a new message each time
            # first, attempt to delete the start-up message if it exists
            try:
                await previous_message.delete()
            except Exception as delete_exception:
                debug(f"Failed to delete old (specified) message: {delete_exception}")
                await self.tautulli_channel.purge(check=self.is_me)
            # send new message
            debug("Using new message...")
            if not activity or data_wrapper.error:
                # error when refreshing Tautulli data, new_message is string (i.e. "Connection lost")
                debug("Sending new message with Tautulli error...")
            else:
                debug('Sending new message...')
            # send a new message, regardless of whether the content has changed
            new_message = await send_message(content=data_wrapper, channel=self.tautulli_channel,
                                             embed=self.use_embeds)

        if data_wrapper.plex_pass:
            await add_emoji_number_reactions(message=new_message, count=count)

            # check to see if the user clicked a reaction *while* they were being added
            cache_msg = await new_message.channel.fetch_message(new_message.id)
            for reaction in cache_msg.reactions:
                if reaction.count > 1:
                    async for user in reaction.users():
                        if user.id == self.owner_id:
                            loc = statics.emoji_numbers.index(str(reaction.emoji))
                            debug(f"Stopping stream {loc}...")
                            stopped_message = self.tautulli.stop_stream(stream_number=loc)
                            info(stopped_message)
                            end_notification = await self.tautulli_channel.send(content=stopped_message)
                            await asyncio.sleep(self.refresh_time)
                            await end_notification.delete()
                            await new_message.clear_reaction(str(reaction.emoji))
                            return new_message

            def check(reaction, user):
                return user.id == self.owner_id and reaction.message.id == new_message.id and str(
                    reaction.emoji) in statics.emoji_numbers

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=float(self.refresh_time),
                                                            check=check)
            except asyncio.TimeoutError as e:
                pass
            else:
                loc = statics.emoji_numbers.index(str(reaction.emoji))
                debug(f"Stopping stream {loc}...")
                stopped_message = self.tautulli.stop_stream(stream_number=loc)
                info(stopped_message)
                end_notification = await self.tautulli_channel.send(content=stopped_message)
                await asyncio.sleep(self.refresh_time)
                await end_notification.delete()
                await new_message.clear_reaction(str(reaction.emoji))
        else:
            await asyncio.sleep(self.refresh_time)
        return new_message

    async def get_tautulli_channel(self) -> None:
        info(f"Getting {self.tautulli_channel_name} channel")
        self.tautulli_channel: discord.TextChannel = \
            await self.get_discord_channel_by_name(channel_name=self.tautulli_channel_name)
        if not self.tautulli_channel:
            raise Exception(f"Could not load {self.tautulli_channel_name} channel. Exiting...")
        info(f"{self.tautulli_channel_name} channel collected.")

    async def get_discord_channel_by_starting_name(self, starting_channel_name: str, channel_type: str = "text") -> \
            Union[discord.VoiceChannel, discord.TextChannel]:
        for channel in self.client.get_all_channels():
            if channel.name.startswith(starting_channel_name):
                return channel
        try:
            guild = self.client.get_guild(self.guild_id)  # stupid positional-only parameters
            if channel_type == 'voice':
                return await guild.create_voice_channel(name=starting_channel_name)
            else:
                return await guild.create_text_channel(name=starting_channel_name)
        except:
            raise Exception(f"Could not create channel {starting_channel_name}")

    async def get_discord_channel_by_name(self, channel_name: str, channel_type: str = "text") -> \
            Union[discord.VoiceChannel, discord.TextChannel]:
        for channel in self.client.get_all_channels():
            if channel.name == channel_name:
                return channel
        error(f"Could not load {channel_name} channel. Attempting to create...")
        try:
            guild = self.client.get_guild(self.guild_id)  # stupid positional-only parameters
            if channel_type == 'voice':
                return await guild.create_voice_channel(name=channel_name)
            else:
                return await guild.create_text_channel(name=channel_name)
        except:
            raise Exception(f"Could not create channel {channel_name}")

    async def edit_library_voice_channel(self, channel_name: str, count: int) -> None:
        info(f"Updating {channel_name} voice channel with new library size")
        channel = await self.get_discord_channel_by_starting_name(starting_channel_name=f"{channel_name}:",
                                                                  channel_type="voice")
        if not channel:
            error(f"Could not load {channel_name} channel")
        else:
            try:
                await channel.edit(name=f"{channel_name}: {count}")
            except Exception as voice_channel_edit_error:
                pass

    async def edit_bandwidth_voice_channel(self, channel_name: str, size: int) -> None:
        info(f"Updating {channel_name} voice channel with new bandwidth")
        channel = await self.get_discord_channel_by_starting_name(starting_channel_name=f"{channel_name}:",
                                                                  channel_type="voice")
        if not channel:
            error(f"Could not load {channel_name} channel")
        else:
            try:
                await channel.edit(name=f"{channel_name}: {size}")
            except Exception as voice_channel_edit_error:
                pass

    async def edit_stream_count_voice_channel(self, channel_name: str, count: int) -> None:
        info(f"Updating {channel_name} voice channel with new stream count")
        channel = await self.get_discord_channel_by_starting_name(starting_channel_name=f"{channel_name}:",
                                                                  channel_type="voice")
        if not channel:
            error(f"Could not load {channel_name} channel")
        else:
            try:
                await channel.edit(name=f"{channel_name}: {count}")
            except Exception as voice_channel_edit_error:
                pass

    async def get_old_message_in_tautulli_channel(self) -> discord.Message:
        """
        Get the last message sent in the Tautulli channel, used to start the bot loop
        :return: discord.Message
        """
        # If the very last message in the channel is from Tauticord, use it
        async for msg in self.tautulli_channel.history(limit=1):
            if msg.author == self.client.user:
                await msg.clear_reactions()
                return msg
        # If the very last message in the channel is not from Tauticord, make a new one.
        info("Couldn't find old message, sending initial message...")
        return await send_starter_message(tautulli_connector=self.tautulli, discord_channel=self.tautulli_channel)

    async def update_voice_channels(self, activity) -> None:
        if activity:
            if self.tautulli.voice_channel_settings.get('count', False):
                await self.edit_stream_count_voice_channel(channel_name="Current Streams", count=activity.stream_count)
            if self.tautulli.voice_channel_settings.get('transcodes', False):
                await self.edit_stream_count_voice_channel(channel_name="Current Transcodes",
                                                           count=activity.transcode_count)
            if self.tautulli.voice_channel_settings.get('bandwidth', False):
                await self.edit_bandwidth_voice_channel(channel_name="Bandwidth", size=activity.total_bandwidth)
            if self.tautulli.voice_channel_settings.get('localBandwidth', False):
                await self.edit_bandwidth_voice_channel(channel_name="Local Bandwidth",
                                                        size=activity.lan_bandwidth)
            if self.tautulli.voice_channel_settings.get('remoteBandwidth', False):
                await self.edit_bandwidth_voice_channel(channel_name="Remote Bandwidth",
                                                        size=activity.wan_bandwidth)

    @tasks.loop(hours=1.0)
    async def update_libraries(self) -> None:
        if self.tautulli.voice_channel_settings.get('stats', False):
            for library_name in self.tautulli.voice_channel_settings.get('libraries', []):
                size = self.tautulli.get_library_item_count(library_name=library_name)
                await self.edit_library_voice_channel(channel_name=library_name, count=size)
