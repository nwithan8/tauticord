from typing import List, Union

import discord

import modules.statics as statics
from modules.discord.services.base_service import BaseService
from modules.emojis import EmojiManager


def build_response(message: discord.Message, bot_id: int, admin_ids: List[int]) -> Union[str, None]:
    # If message does not mention the bot, return None
    if bot_id not in [user.id for user in message.mentions]:
        return None

    author_id = str(message.author.id)
    if author_id == "DISCORDIDADDEDBYGITHUB":
        return "Hello, creator!"

    if author_id not in [str(admin_id) for admin_id in admin_ids]:
        return None

    # Message mentions the bot and is from an admin
    return statics.INFO_SUMMARY


class TaggedMessagesManager(BaseService):
    """
    A service that manages how to bot interacts with tagged messages. Starts running when the bot is ready.
    """

    def __init__(self, guild_id: int,
                 emoji_manager: EmojiManager,
                 admin_ids: list[int] = None):
        super().__init__()
        self.guild_id = guild_id
        self.admin_ids = admin_ids or []
        self.emoji_manager = emoji_manager

    async def associate_bot_callbacks(self):
        # noinspection PyAttributeOutsideInit
        self.on_message = self.bot.event(self.on_message)

    async def enabled(self) -> bool:
        return True

    async def on_ready(self):
        pass

    async def on_message(self, message: discord.Message) -> None:
        response = build_response(message=message, bot_id=self.bot.user.id, admin_ids=self.admin_ids)

        if response:
            await message.channel.send(response)
