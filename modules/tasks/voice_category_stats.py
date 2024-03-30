import asyncio
from typing import Union, Callable

import discord

import modules.logs as logging
from modules.discord import discord_utils
from modules.settings.models import VoiceChannel


class VoiceCategoryStatsMonitor:
    def __init__(self,
                 discord_client,
                 guild_id: int,
                 service_entrypoint: Callable,
                 voice_category: discord.CategoryChannel = None):
        self.discord_client = discord_client
        self.guild_id = guild_id
        self.voice_category = voice_category
        self.service_entrypoint = service_entrypoint

    async def run_service(self, interval_seconds: int) -> None:
        if not self.voice_category:
            return  # No performance voice category set, so don't bother

        while True:
            try:
                await self.service_entrypoint()
                await asyncio.sleep(interval_seconds)
            except Exception:
                exit(1)  # Die on any unhandled exception for this subprocess (i.e. internet connection loss)

    async def edit_stat_voice_channel(self,
                                      voice_channel_settings: VoiceChannel,
                                      stat: Union[int, float, str]) -> None:
        channel = None

        if voice_channel_settings.channel_id_set:
            channel_id = voice_channel_settings.channel_id
            channel = await self.discord_client.fetch_channel(channel_id)
            if not channel:
                logging.error(f"Could not load channel with ID {channel_id}")
        else:
            partial_channel_name = voice_channel_settings.prefix
            try:
                channel = await discord_utils.get_or_create_discord_channel_by_starting_name(client=self.discord_client,
                                                                                             guild_id=self.guild_id,
                                                                                             starting_channel_name=f"{partial_channel_name}",
                                                                                             channel_type=discord.ChannelType.voice,
                                                                                             category=self.voice_category)
            except Exception as e:
                logging.error(f"Error editing {partial_channel_name} voice channel: {e}")
                return

        try:
            new_name = voice_channel_settings.build_channel_name(value=stat)
            await channel.edit(name=f"{new_name}")
            logging.info(f"Updated {channel.name} successfully")
        except Exception as voice_channel_edit_error:
            logging.error(f"Error editing {channel.name} voice channel: {voice_channel_edit_error}")
