from collections.abc import Callable
from typing import Union, List, Optional

import discord

import modules.logs as logging
from modules.utils import quote, strip_phantom_space


async def get_guild(client: discord.Client, guild_id: int) -> discord.Guild:
    guild = client.get_guild(guild_id)
    if not guild:
        raise Exception(f"Could not load guild with ID {guild_id}")
    return guild


async def available_emoji_slots(client: discord.Client, guild_id: int) -> int:
    guild = await get_guild(client=client, guild_id=guild_id)
    return max([guild.emoji_limit - len(guild.emojis), 0])  # Somehow this number can be negative


async def filter_emoji_list_to_non_existent(client: discord.Client, guild_id: int, emoji_names: List[str]) -> List[str]:
    guild = await get_guild(client=client, guild_id=guild_id)
    guild_emojis = [emoji.name for emoji in guild.emojis]
    return [emoji_name for emoji_name in emoji_names if emoji_name not in guild_emojis]


async def create_discord_text_channel(client: discord.Client,
                                      guild_id: int,
                                      channel_name: str,
                                      category: discord.CategoryChannel = None) -> discord.TextChannel:
    guild = await get_guild(client=client, guild_id=guild_id)
    return await guild.create_text_channel(name=channel_name, category=category)


async def create_discord_voice_channel(client: discord.Client,
                                       guild_id: int,
                                       channel_name: str,
                                       category: discord.CategoryChannel = None) -> discord.VoiceChannel:
    guild = await get_guild(client=client, guild_id=guild_id)
    return await guild.create_voice_channel(name=channel_name, category=category)


async def create_discord_category(client: discord.Client,
                                  guild_id: int,
                                  channel_name: str) -> discord.CategoryChannel:
    guild = await get_guild(client=client, guild_id=guild_id)
    return await guild.create_category(name=channel_name)


async def create_discord_channel(client: discord.Client,
                                 guild_id: int,
                                 channel_name: str,
                                 channel_type: discord.ChannelType,
                                 category: discord.CategoryChannel = None) -> \
        Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]:
    match channel_type:
        case discord.ChannelType.voice:
            return await create_discord_voice_channel(client=client,
                                                      guild_id=guild_id,
                                                      channel_name=channel_name,
                                                      category=category)
        case discord.ChannelType.text:
            return await create_discord_text_channel(client=client,
                                                     guild_id=guild_id,
                                                     channel_name=channel_name,
                                                     category=category)
        case discord.ChannelType.category:
            return await create_discord_category(client=client,
                                                 guild_id=guild_id,
                                                 channel_name=channel_name)


async def get_all_discord_channels(client: discord.Client,
                                   guild_id: int,
                                   channel_type: discord.ChannelType = None) -> List[
    Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]]:
    guild = await get_guild(client=client, guild_id=guild_id)

    if not channel_type:
        guild = await get_guild(client=client, guild_id=guild_id)
        return [channel for channel in guild.channels]

    match channel_type:
        case discord.ChannelType.voice:
            return [channel for channel in guild.voice_channels]
        case discord.ChannelType.text:
            return [channel for channel in guild.text_channels]
        case discord.ChannelType.category:
            return [channel for channel in guild.categories]
        case _:
            raise ValueError(f"Invalid channel type: {channel_type}")


async def get_or_create_discord_channel_by_name(client: discord.Client,
                                                guild_id: int,
                                                channel_name: str,
                                                channel_type: discord.ChannelType,
                                                category: discord.CategoryChannel = None) -> \
        Union[discord.VoiceChannel, discord.TextChannel, discord.CategoryChannel, None]:
    channel_name_normalized = normalize_channel_name(channel_name=channel_name)
    channels = await get_all_discord_channels(client=client, guild_id=guild_id, channel_type=channel_type)
    for channel in channels:
        if normalize_channel_name(channel_name=channel.name) == channel_name_normalized:
            if category and channel.category != category:
                continue
            return channel

    logging.error(f"Could not load {channel_name} channel. Attempting to create...")
    return await create_discord_channel(client=client,
                                        guild_id=guild_id,
                                        channel_name=channel_name,
                                        channel_type=channel_type,
                                        category=category)


async def get_or_create_discord_channel_by_starting_name(client: discord.Client,
                                                         guild_id: int,
                                                         starting_channel_name: str,
                                                         channel_type: discord.ChannelType,
                                                         category: discord.CategoryChannel = None) -> \
        Union[discord.VoiceChannel, discord.TextChannel, None]:
    starting_channel_name_normalized = normalize_channel_name(channel_name=starting_channel_name)
    channels = await get_all_discord_channels(client=client, guild_id=guild_id, channel_type=channel_type)
    for channel in channels:
        name_normalized = normalize_channel_name(channel_name=channel.name)

        if name_normalized.startswith(starting_channel_name_normalized):
            if category and channel.category != category:
                continue
            return channel

    logging.error(f"Could not load {starting_channel_name} channel. Attempting to create...")
    return await create_discord_channel(client=client,
                                        guild_id=guild_id,
                                        channel_name=starting_channel_name,
                                        channel_type=channel_type,
                                        category=category)


async def get_or_create_discord_category_by_name(client: discord.Client,
                                                 guild_id: int,
                                                 category_name: str) -> discord.CategoryChannel:
    logging.debug(f"Getting {quote(category_name)} category")
    category_name_normalized = normalize_category_name(category_name=category_name)
    categories = await get_all_discord_channels(client=client, guild_id=guild_id,
                                                channel_type=discord.ChannelType.category)
    for category in categories:
        if normalize_category_name(category_name=category.name) == category_name_normalized:
            return category

    logging.error(f"Could not load {category_name} category. Attempting to create...")
    return await create_discord_category(client=client,
                                         guild_id=guild_id,
                                         channel_name=category_name)


async def delete_all_channel_messages(channel: discord.TextChannel) -> None:
    """
    Delete all messages in a text channel.
    :param channel: Channel to delete messages from
    :return: None
    """
    await channel.purge()


async def get_very_last_message_in_channel(channel: discord.TextChannel, validators: list[Callable[[discord.Message], bool]] = None) -> Optional[discord.Message]:
    """
    Get the very last message in a text channel.
    :param channel: Channel to get the message from
    :param validators: List of validation functions to check the message against. Each function should take a discord.Message as input and return a boolean.
    :return: The very last message in the channel if all validators passed, else None
    """
    return await get_most_recent_message_in_channel_matching_validators(channel=channel, validators=validators or [], max_depth=1)


async def get_most_recent_message_in_channel_matching_validators(channel: discord.TextChannel, validators: list[Callable[[discord.Message], bool]], max_depth: int = 50) -> Optional[discord.Message]:
    """
    Get the most recent message in a text channel that matches all validators.
    :param channel: Channel to get the message from
    :param validators: List of validation functions to check the message against. Each function should take a discord.Message as input and return a boolean.
    :param max_depth: Maximum number of messages to search through
    :return: The most recent message in the channel that matches all validators, else None
    """
    async for msg in channel.history(limit=max_depth):
        msg.embeds[0].footer.text
        if all(validator(msg) for validator in validators):
            return msg

    return None

async def send_text_message(text: str = None,
                            message: discord.Message = None,
                            channel: discord.TextChannel = None):
    """
    Send or edit a message with text.
    :param text: Text to send
    :param message: Message to edit
    :param channel: Channel to send the message to
    :return: Message sent
    """
    # if neither channel nor message is specified, throw an error
    if not channel and not message:
        raise ValueError("Must specify either a channel or a message")
    if message:  # if message exists, use it to edit the message
        if not text:  # oops, no text to send
            await message.edit(content="Something went wrong.", embed=None)
        else:
            await message.edit(content=text, embed=None)
        return message
    else:  # otherwise, send a new message in the channel
        if not text:  # oops, no text to send
            return await channel.send(content="Something went wrong.")
        else:
            return await channel.send(content=text)


async def send_embed_message(embed: discord.Embed = None,
                             message: discord.Message = None,
                             channel: discord.TextChannel = None):
    """
    Send or edit a message with an embed.
    :param embed: Embed to send
    :param message: Message to edit
    :param channel: Channel to send the message to
    :return: Message sent
    """
    # if neither channel nor message is specified, throw an error
    if not channel and not message:
        raise ValueError("Must specify either a channel or a message")
    if message:  # if message exists, use it to edit the message
        if not embed:  # oops, no embed to send
            await message.edit(content="Something went wrong.", embed=None)  # erase any existing content and embeds
        else:
            await message.edit(content=None, embed=embed)  # erase any existing content and embeds
        return message
    else:  # otherwise, send a new message in the channel
        if not embed:  # oops, no embed to send
            return await channel.send(content="Something went wrong.")
        else:
            return await channel.send(content=None, embed=embed)


async def send_view_message(view: discord.ui.View = None,
                            message: discord.Message = None,
                            channel: discord.TextChannel = None):
    """
    Send or edit a message with a View.
    :param view: View to send
    :param message: Message to edit
    :param channel: Channel to send the message to
    :return: Message sent
    """
    # if neither channel nor message is specified, throw an error
    if not channel and not message:
        raise ValueError("Must specify either a channel or a message")
    if message:  # if message exists, use it to edit the message
        if not view:  # oops, no view to send
            await message.edit(content="Something went wrong.", view=None)  # erase any existing content and views
        else:
            await message.edit(content=None, view=view)  # erase any existing content and views
        return message
    else:  # otherwise, send a new message in the channel
        if not view:  # oops, no view to send
            return await channel.send(content="Something went wrong.")
        else:
            return await channel.send(content=None, view=view)


async def respond_to_slash_command_with_text(interaction: discord.Interaction, text: str, ephemeral: bool = False):
    """
    Respond to a slash command with text.
    :param interaction: Interaction to respond to
    :param text: Text to send
    :param ephemeral: Whether the response should be ephemeral
    :return: Message sent
    """
    return await interaction.response.send_message(text, ephemeral=ephemeral)


async def respond_to_slash_command_with_view(interaction: discord.Interaction, view: discord.ui.View,
                                             ephemeral: bool = False):
    """
    Respond to a slash command with a View.
    :param interaction: Interaction to respond to
    :param view: View to send
    :param ephemeral: Whether the response should be ephemeral
    :return: Message sent
    """
    try:
        # Try to respond to the interaction
        return await interaction.response.send_message(view=view, ephemeral=ephemeral)
    except discord.errors.InteractionResponded:
        # If the interaction has already been responded to (e.g. with a "thinking" placeholder), then get the original response message
        return await interaction.edit_original_response(view=view)


async def respond_to_slash_command_with_embed(interaction: discord.Interaction, embed: discord.Embed,
                                              ephemeral: bool = False):
    """
    Respond to a slash command with an embed.
    :param interaction: Interaction to respond to
    :param embed: Embed to send
    :param ephemeral: Whether the response should be ephemeral
    :return: Message sent
    """
    try:
        # Try to respond to the interaction
        return await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    except discord.errors.InteractionResponded:
        # If the interaction has already been responded to (e.g. with a "thinking" placeholder), then get the original response message
        return await interaction.edit_original_response(embed=embed)


async def respond_to_slash_command_with_file(interaction: discord.Interaction, file: discord.File,
                                             ephemeral: bool = False):
    """
    Respond to a slash command with a file.
    :param interaction: Interaction to respond to
    :param file: File to send
    :param ephemeral: Whether the response should be ephemeral
    :return: Message sent
    """
    return await interaction.response.send_message(file=file, ephemeral=ephemeral)


async def respond_to_slash_command_with_thinking(interaction: discord.Interaction, ephemeral: bool = True) -> None:
    """
    Send a "thinking" placeholder response to a slash command.
    :param interaction: Interaction to respond to
    :param ephemeral: Whether the response should be ephemeral
    :return: None
    """
    await interaction.response.defer(thinking=True, ephemeral=ephemeral)


async def defer_slash_command_response(interaction: discord.Interaction) -> None:
    """
    Defer a slash command response. Use to process a command for longer than 3 seconds.
    :param interaction: Interaction to defer the response for
    :return: None
    """
    await interaction.response.defer()


async def update_presence(client: discord.Client,
                          line_one: str,
                          activity_name: Optional[str] = None,
                          large_image: Optional[str] = None,
                          large_image_text: Optional[str] = None,
                          small_image: Optional[str] = None,
                          small_image_text: Optional[str] = None,
                          status: Optional[discord.Status] = discord.Status.online):
    # ref: https://discord.com/developers/docs/rich-presence/how-to#updating-presence-update-presence-payload-fields
    # ref: https://discord.com/developers/docs/game-sdk/activities#updateactivity
    use_custom_activity_type = activity_name is None
    if use_custom_activity_type:
        activity_type = discord.ActivityType.custom
        # For a custom message, all three fields need to be populated
        name = line_one
        details = line_one
        state = line_one
    else:
        activity_type = discord.ActivityType.watching
        name = activity_name
        details = None
        state = line_one

    activity = discord.Activity(
        name=name,
        type=activity_type,
        details=details,
        state=state,
        assets={
            'large_image': large_image,
            'large_text': large_image_text,
            'small_image': small_image,
            'small_text': small_image_text
        }
    )
    await client.change_presence(activity=activity, status=status)


def is_valid_reaction(reaction_emoji: discord.PartialEmoji,
                      reaction_user_id: int,
                      reaction_message: discord.Message,
                      reaction_type: str,
                      valid_reaction_type: str = None,
                      valid_message: discord.Message = None,
                      valid_emojis: List[str] = None,
                      valid_user_ids: List[int] = None,
                      skip_self_reaction: bool = True) -> bool:
    if skip_self_reaction and reaction_user_id == valid_message.author.id:
        return False
    if valid_reaction_type and reaction_type != valid_reaction_type:
        return False
    if valid_message and reaction_message.id != valid_message.id:
        return False
    if valid_emojis and str(reaction_emoji) not in valid_emojis:
        return False
    if valid_user_ids and reaction_user_id not in valid_user_ids:
        return False
    return True


def normalize_channel_name(channel_name: str) -> str:
    """
    Normalize a Discord channel name.
    :param channel_name: The original channel name
    :return: Normalized channel name
    """
    channel_name = channel_name.strip()  # Remove leading and trailing spaces
    channel_name = strip_phantom_space(string=channel_name)  # Remove phantom spaces
    channel_name = channel_name.replace(" ", "")  # Remove any weird space characters in the name
    channel_name = channel_name.lower()
    return channel_name


def normalize_category_name(category_name: str) -> str:
    """
    Normalize a Discord category name.
    :param category_name: The original category name
    :return: Normalized category name
    """
    category_name = category_name.strip()  # Remove leading and trailing spaces
    category_name = strip_phantom_space(string=category_name)  # Remove phantom spaces
    category_name = category_name.replace(" ", "")  # Remove any weird space characters in the name
    category_name = category_name.lower()
    return category_name
