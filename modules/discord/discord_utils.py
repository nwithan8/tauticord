from typing import Union, List, Optional

import discord

import modules.logs as logging
from modules.utils import quote


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
    channels = await get_all_discord_channels(client=client, guild_id=guild_id, channel_type=channel_type)
    for channel in channels:
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


async def get_or_create_discord_channel_by_starting_name(client: discord.Client,
                                                         guild_id: int,
                                                         starting_channel_name: str,
                                                         channel_type: discord.ChannelType,
                                                         category: discord.CategoryChannel = None) -> \
        Union[discord.VoiceChannel, discord.TextChannel, None]:
    channels = await get_all_discord_channels(client=client, guild_id=guild_id, channel_type=channel_type)
    for channel in channels:
        name = channel.name.strip()  # Phantom spaces are the worst

        if name.startswith(starting_channel_name):
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
    logging.info(f"Getting {quote(category_name)} category")
    categories = await get_all_discord_channels(client=client, guild_id=guild_id,
                                                channel_type=discord.ChannelType.category)
    for category in categories:
        if category.name == category_name:
            return category

    logging.error(f"Could not load {category_name} category. Attempting to create...")
    return await create_discord_category(client=client,
                                         guild_id=guild_id,
                                         channel_name=category_name)


async def send_embed_message(embed: discord.Embed = None, message: discord.Message = None,
                             channel: discord.TextChannel = None):
    """
    Send or edit a message.
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
        name = line_one
        details = None
        state = None
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
