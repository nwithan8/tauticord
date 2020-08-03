import discord
import modules.vars as vars
import asyncio
from modules.logs import *
import sys


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
    # await tautulli_channel.send(content="Hello world!") #<---- UNCOMMENT AND RUN ONCE
    message = await discord_connector.get_old_message_in_tautulli_channel()
    while True:
        message = await discord_connector.edit_message(previous_message=message)


async def add_emoji_number_reactions(message, count):
    """
    Add number reactions to a message for user interaction
    :param message: message to add emojis to
    :param count: how many emojis to add
    :return: None
    """
    for i in range(0, count):
        await message.add_reaction(vars.emoji_numbers[i])


class DiscordConnector:
    def __init__(self, token, owner_id, refresh_time, tautulli_channel_id, tautulli_connector, analytics):
        self.token = token
        self.owner_id = owner_id
        self.refresh_time = refresh_time
        self.tautulli_channel_id = tautulli_channel_id
        self.tautulli_channel = None
        self.tautulli = tautulli_connector
        self.analytics = analytics
        self.client = discord.Client()
        self.on_ready = self.client.event(self.on_ready)

    async def on_ready(self):
        info('Connected to Discord.')
        await start_bot(discord_connector=self, analytics=self.analytics)

    def connect(self):
        info('Connecting to Discord...')
        self.client.run(self.token)

    async def edit_message(self, previous_message):
        """
        Collect new summary info, replace old message with new one
        :param previous_message: discord.Message to replace
        :return: new discord.Message
        """
        new_message, count = self.tautulli.refresh_data()
        await previous_message.delete()
        new_message = await self.tautulli_channel.send(content=new_message)
        await add_emoji_number_reactions(message=new_message, count=count)
        bot_owner = self.client.get_user(self.owner_id)
        reaction = ""
        user = ""

        def check(reaction, user):
            return user == bot_owner

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=float(self.refresh_time), check=check)
        except asyncio.TimeoutError as e:
            info(e)
            pass
        if reaction:
            if user.id == self.owner_id:
                loc = vars.emoji_numbers.index(str(reaction.emoji))
                stopped_message = self.tautulli.stop_stream(stream_number=loc)
                info(stopped_message)
                end_notification = await self.tautulli_channel.send(content=stopped_message)
                await end_notification.delete(delay=1.0)
        return new_message

    async def get_tautulli_channel(self):
        info(f"Getting channel ID {self.tautulli_channel_id}")
        self.tautulli_channel = self.client.get_channel(self.tautulli_channel_id)
        info(f"Channel ID {self.tautulli_channel_id} collected.")
        return self.tautulli_channel

    async def get_old_message_in_tautulli_channel(self):
        """
        Get the last message sent in the Tautulli channel, used to start the bot loop
        :return: discord.Message
        """
        last_bot_message_id = ""
        while last_bot_message_id == "":
            async for msg in self.tautulli_channel.history(limit=100):
                if msg.author == self.client.user:
                    last_bot_message_id = msg.id
                    break
            if last_bot_message_id == "":
                info("Couldn't find old message, sending 'Hello world!'")
                await self.tautulli_channel.send(content="Hello world!")
        return await self.tautulli_channel.fetch_message(last_bot_message_id)
