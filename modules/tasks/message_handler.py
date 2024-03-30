from typing import List, Union

import discord

from modules import statics


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


class MessageHandler:
    def __init__(self, client: discord.Client, admin_ids: List[int]):
        self.client = client
        self.admin_ids = admin_ids

    async def on_message(self, message: discord.Message) -> None:
        response = build_response(message=message, bot_id=self.client.user.id, admin_ids=self.admin_ids)

        if response:
            await message.channel.send(response)
