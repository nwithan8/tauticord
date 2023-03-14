import logging
from pathlib import Path
from typing import Optional, Union

import discord
from discord import Emoji

stream_number_emojis = [
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "🇦",
    "🇧",
    "🇨",
    "🇩",
    "🇪",
    "🇫",
    "🇬",
    "🇭",
    "🇮",
    "🇯",
    "🇰",
    "🇱",
    "🇲",
    "🇳",
    "🇴",
    "🇵",
    "🇶",
    "🇷",
    "🇸",
    "🇹",
    "🇺",
    "🇻",
    "🇼",
    "🇽",
    "🇾",
    "🇿",
]


async def upload_new_emoji(file: str, name: str, client: discord.Client, guild_id: str) -> Union[discord.Emoji, None]:
    # guild ID is a string the whole time until here, we'll see how they account for int overflow in the future
    guild = client.get_guild(int(guild_id))  # stupid positional-only parameters

    # Upload the new emoji
    try:
        with open(file, 'rb') as f:
            image_bytes: bytes = f.read()
            return await guild.create_custom_emoji(name=name, image=image_bytes, reason="Tauticord emoji upload")
    except Exception as e:
        logging.error(f"Failed to upload emoji {name} to server: {e}. Will use default emoji instead.")
        return None


async def collect_guild_emojis(client: discord.Client, guild_id: str) -> tuple[Emoji, ...]:
    # guild ID is a string the whole time until here, we'll see how they account for int overflow in the future
    guild = client.get_guild(int(guild_id))  # stupid positional-only parameters

    return guild.emojis


def max_controllable_stream_count_supported(max_streams_override: Optional[int] = None) -> int:
    return max_streams_override or len(stream_number_emojis)


def emoji_from_stream_number(number):
    return stream_number_emojis[number - 1]


def stream_number_from_emoji(emoji):
    return stream_number_emojis.index(str(emoji)) + 1


class EmojiManager:
    def __init__(self) -> None:
        self._emoji_prefix = "tc"
        # Define the default emojis here
        self._emojis = {
            "bandwidth": "📶",
            "buffering": "⏳",
            "clip": "🎞",
            "episode": "🧩",
            "episodes": "🧩",
            "error": "⚠️",
            "home": "🏠",
            "live": "📡",
            "movie": "🎥",
            "movies": "🎥",
            "paused": "⏸",
            "person": "👤",
            "photo": "🖼",
            "playing": "▶️",
            "stopped": "⏹",
            "device": "📱",
            "resolution": "🖥",
            "progress": "⏰",
            "series": "📺",
            "artist": "🎤",
            "artists": "🎤",
            "track": "🎵",
            "tracks": "🎵",
        }

    async def load_emojis(self, source_folder: str, client: discord.Client, guild_id: str) -> None:
        # Upload PNG emojis from the emoji folder
        for file in Path(source_folder).glob("*.png"):
            await self.add_new_emoji(file=str(file), client=client, guild_id=guild_id)

    async def add_new_emoji(self, file: str, client: discord.Client, guild_id: str, name: Optional[str] = None) -> None:
        name = name or Path(file).stem
        name_with_prefix = f"{self._emoji_prefix}_{name}"

        # Check if the emoji already exists
        existing_emojis = await collect_guild_emojis(client=client, guild_id=guild_id)
        for emoji in existing_emojis:
            if emoji.name == name_with_prefix:
                # Store the emoji in the cache if it already exists
                self._emojis[name] = f"<:{name_with_prefix}:{emoji.id}>"
                return

        # Upload the new emoji
        emoji = await upload_new_emoji(file=file, name=name_with_prefix, client=client, guild_id=guild_id)

        if not emoji:  # Emoji upload failed
            return  # Keep the default emoji

        # Store the new emoji in the cache
        self._emojis[name] = f"<:{name_with_prefix}:{emoji.id}>"
        return

    def get_emoji(self, key: str) -> str:
        try:
            return self._emojis[key]
        except KeyError:
            return ""
