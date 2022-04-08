import asyncio
import sys

import discord
from discord.ext import tasks

import modules.statics as statics
from modules.logs import *


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


async def send_starter_message(tautulli_connector, discord_channel):
    if tautulli_connector.use_embeds:
        embed = discord.Embed(title="Welcome to Tauticord!")
        embed.add_field(name="Starting up...",
                        value='This will be replaced once we get data.',
                        inline=False)
        await discord_channel.send(embed=embed)
    else:
        await discord_channel.send(content="Welcome to Tauticord!")


async def send_message(content=None, embed: discord.Embed = None, message: discord.Message = None,
                       channel: discord.TextChannel = None):
    """
    Send or edit a message.
    :param content: Contents of the message to send
    :param embed: Embed to send
    :param message: Message to edit
    :param channel: Channel to send the message to
    :return: Message sent
    """
    # if neither channel nor message is specified, throw an error
    if not channel and not message:
        raise ValueError("Must specify either a channel or a message")
    if message:  # if message exists, use it to edit the message
        await message.edit(content=content, embed=embed)
        return message
    else:  # otherwise, send a new message in the channel
        return await channel.send(content=content, embed=embed)


class DiscordConnector:
    def __init__(self,
                 token: str,
                 guild_id: int,
                 owner_id: int,
                 refresh_time: int,
                 tautulli_channel_name: str,
                 tautulli_connector,
                 analytics,
                 use_embeds: bool):
        self.token = token
        self.guild_id = guild_id
        self.owner_id = owner_id
        self.refresh_time = refresh_time
        self.tautulli_channel_name = tautulli_channel_name
        self.tautulli_channel = None
        self.tautulli = tautulli_connector
        self.analytics = analytics
        self.use_embeds = use_embeds
        self.client = discord.Client()
        self.on_ready = self.client.event(self.on_ready)

    async def on_ready(self):
        info('Connected to Discord.')
        self.update_libraries.start()
        await start_bot(discord_connector=self, analytics=self.analytics)

    def connect(self):
        info('Connecting to Discord...')
        self.client.run(self.token)

    def is_me(self, message):
        return message.author == self.client.user

    async def edit_message(self, previous_message):
        """
        Collect new summary info, replace old message with new one
        :param previous_message: discord.Message to replace
        :return: new discord.Message
        """
        new_message, count, activity = self.tautulli.refresh_data()

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
            if not activity:
                # error when refreshing Tautulli data, new_message is string (i.e. "Connection lost")
                debug("Editing old message with Tautulli error...")
                new_message = await send_message(content=new_message, message=previous_message)
                # edit the previous message, regardless of whether the content has changed
            else:
                # update the message regardless of whether the content has changed
                debug('Editing old message...')
                new_message = await send_message(content=None if self.use_embeds else new_message,
                                                 embed=new_message if self.use_embeds else None,
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
            if not activity:
                # error when refreshing Tautulli data, new_message is string (i.e. "Connection lost")
                debug("Sending new message with Tautulli error...")
                new_message = await send_message(content=new_message, channel=self.tautulli_channel)
                # send a new message, regardless of whether the content has changed
            else:
                # send a new message, regardless of whether the content has changed
                debug('Sending new message...')
                new_message = await send_message(content=None if self.use_embeds else new_message,
                                                 embed=new_message if self.use_embeds else None,
                                                 channel=self.tautulli_channel)

        if self.tautulli.plex_pass:
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
                            await asyncio.sleep(min([5, self.refresh_time]))
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
                await asyncio.sleep(min([5, self.refresh_time]))
                await end_notification.delete()
                await new_message.clear_reaction(str(reaction.emoji))
        else:
            await asyncio.sleep(self.refresh_time)
        return new_message

    async def get_tautulli_channel(self):
        info(f"Getting {self.tautulli_channel_name} channel")
        self.tautulli_channel = await self.get_discord_channel_by_name(channel_name=self.tautulli_channel_name)
        if not self.tautulli_channel:
            raise Exception(f"Could not load {self.tautulli_channel_name} channel. Exiting...")
        info(f"{self.tautulli_channel_name} channel collected.")

    async def get_discord_channel_by_starting_name(self, starting_channel_name: str, channel_type: str = "text"):
        for channel in self.client.get_all_channels():
            if channel.name.startswith(starting_channel_name):
                return channel
        try:
            guild = self.client.get_guild(id=self.guild_id)
            if channel_type == 'voice':
                return await guild.create_voice_channel(name=starting_channel_name)
            else:
                return await guild.create_text_channel(name=starting_channel_name)
        except:
            raise Exception(f"Could not create channel {starting_channel_name}")

    async def get_discord_channel_by_name(self, channel_name: str, channel_type: str = "text"):
        for channel in self.client.get_all_channels():
            if channel.name == channel_name:
                return channel
        error(f"Could not load {channel_name} channel. Attempting to create...")
        try:
            guild = self.client.get_guild(id=self.guild_id)
            if channel_type == 'voice':
                return await guild.create_voice_channel(name=channel_name)
            else:
                return await guild.create_text_channel(name=channel_name)
        except:
            raise Exception(f"Could not create channel {channel_name}")

    async def edit_library_voice_channel(self, channel_name: str, count: int):
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

    async def edit_bandwidth_voice_channel(self, channel_name: str, size: int):
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

    async def edit_stream_count_voice_channel(self, channel_name: str, count: int):
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

    async def get_old_message_in_tautulli_channel(self):
        """
        Get the last message sent in the Tautulli channel, used to start the bot loop
        :return: discord.Message
        """
        last_bot_message_id = ""
        while last_bot_message_id == "":
            async for msg in self.tautulli_channel.history(limit=1):
                print(msg)
                if msg.author == self.client.user:
                    last_bot_message_id = msg.id
                    await msg.clear_reactions()
                    break
            if last_bot_message_id == "":
                info("Couldn't find old message, sending initial message...")
                await send_starter_message(tautulli_connector=self.tautulli, discord_channel=self.tautulli_channel)
        return await self.tautulli_channel.fetch_message(last_bot_message_id)

    async def update_voice_channels(self, activity):
        if activity:
            if self.tautulli.voice_channel_settings.get('count', False):
                await self.edit_stream_count_voice_channel(channel_name="Current Streams", count=activity.stream_count)
            if self.tautulli.voice_channel_settings.get('transcodes', False):
                await self.edit_stream_count_voice_channel(channel_name="Current Transcodes",
                                                           count=activity.transcode_count)
            if self.tautulli.voice_channel_settings.get('bandwidth', False):
                await self.edit_bandwidth_voice_channel(channel_name="Bandwidth", size=activity.total_bandwidth)

    @tasks.loop(hours=1.0)
    async def update_libraries(self):
        if self.tautulli.voice_channel_settings.get('stats', False):
            for library_name in self.tautulli.voice_channel_settings.get('libraries', []):
                size = self.tautulli.get_library_item_count(library_name=library_name)
                await self.edit_library_voice_channel(channel_name=library_name, count=size)
