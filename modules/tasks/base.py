import asyncio
from typing import Union, Callable, Any

import discord

import modules.logs as logging
from modules.discord import discord_utils
from modules.settings.models import VoiceChannel


class ServiceRunner:
    """
    Base class for a cron-based service loop that performs a task at regular intervals.
    """

    def __init__(self,
                 discord_client,
                 guild_id: int,
                 service_entrypoint: Callable,
                 run_service_conditions: list[Callable[['ServiceRunner'], bool]] = None,
                 run_service_error_message: str = None):
        """
        :param discord_client: The Discord client instance.
        :param guild_id: The ID of the Discord guild (server).
        :param service_entrypoint: The async callable to run at each interval.
        :param run_service_conditions: A list of callables that return a boolean indicating whether to run the service.
        :param run_service_error_message: An optional error message to log if conditions are not met.
        """
        self.discord_client = discord_client
        self.guild_id = guild_id
        self.service_entrypoint = service_entrypoint
        self._run_service_conditions = run_service_conditions or []
        self._run_service_error_message = run_service_error_message or "Conditions not met"

    async def run_service(self, interval_seconds: int,
                          additional_conditions: list[Callable[[Any], bool]] = None,
                          override_conditions: list[Callable[[Any], bool]] = None) -> None:
        """
        Initiate the service loop as long as all conditions are met.
        :param interval_seconds: How often to run the service, in seconds.
        :param additional_conditions: Additional conditions to check before each run.
        :param override_conditions: Conditions that, if provided, will replace the default conditions. Will work in conjunction with additional_conditions.
        :return: None
        """
        conditions = override_conditions or self._run_service_conditions
        if additional_conditions:
            conditions += additional_conditions

        if not all(condition(self) for condition in conditions):
            logging.error(f'{self.__class__.__name__}: Service loop conditions not met, {self._run_service_error_message}')
            return

        while True:
            try:
                await self.service_entrypoint()
                await asyncio.sleep(interval_seconds)
            except Exception:
                exit(1)  # Die on any unhandled exception for this subprocess (i.e. internet connection loss)"""


class TextChannelMessageMonitor(ServiceRunner):
    """
    Base class for a cron-based service loop that sends/updates messages to/in a text channel.
    """

    def __init__(self,
                 discord_client,
                 guild_id: int,
                 service_entrypoint: Callable,
                 text_channel: discord.TextChannel = None):
        super().__init__(
            discord_client,
            guild_id,
            service_entrypoint,
            run_service_conditions=[lambda s: s.text_channel is not None],
            run_service_error_message="No text channel set"
        )
        self.text_channel = text_channel

    async def edit_text_message_in_voice_channel(self,
                                                 message: discord.Message,
                                                 new_content: str) -> None:
        if not self.text_channel:
            logging.error("No text channel set to edit message in.")
            return

        try:
            await discord_utils.send_text_message(text=new_content, message=message)
        except Exception as e:
            logging.error(f"Error editing message ID {message.id} in channel {self.text_channel.name}: {e}")

    async def edit_embed_message_in_voice_channel(self,
                                                  message: discord.Message,
                                                  new_embed: discord.Embed) -> None:
        if not self.text_channel:
            logging.error("No text channel set to edit message in.")
            return

        try:
            await discord_utils.send_embed_message(embed=new_embed, message=message)
        except Exception as e:
            logging.error(f"Error editing message ID {message.id} in channel {self.text_channel.name}: {e}")


class VoiceCategoryStatsMonitor(ServiceRunner):
    """
    Base class for a cron-based service loop that updates voice channels in a category with stats.
    """

    def __init__(self,
                 discord_client,
                 guild_id: int,
                 service_entrypoint: Callable,
                 voice_category: discord.CategoryChannel = None):
        super().__init__(
            discord_client,
            guild_id,
            service_entrypoint,
            run_service_conditions=[
                lambda s: s.voice_category is not None,
            ],
            run_service_error_message="No voice category set"
        )
        self.discord_client = discord_client
        self.guild_id = guild_id
        self.voice_category = voice_category
        self.service_entrypoint = service_entrypoint

    async def run_service_override(self, interval_seconds: int, override_voice_channel_check: bool = False) -> None:
        await super().run_service(interval_seconds=interval_seconds,
                                  override_conditions=[lambda s: s.voice_category is not None or override_voice_channel_check])

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
            logging.debug(f"Updated {channel.name} successfully")
        except Exception as voice_channel_edit_error:
            logging.error(f"Error editing {channel.name} voice channel: {voice_channel_edit_error}")
