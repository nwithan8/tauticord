import modules.logs as logging
from pathlib import Path
from typing import Optional, Union, List

import discord
from discord import Emoji, PartialEmoji

from modules import statics


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
    return max_streams_override or statics.MAX_STREAM_COUNT


class EmojiManager:
    def __init__(self) -> None:
        self._emoji_prefix = "tc"
        # Define the default emojis here
        self._emojis = {
            "1": "1️⃣",
            "2": "2️⃣",
            "3": "3️⃣",
            "4": "4️⃣",
            "5": "5️⃣",
            "6": "6️⃣",
            "7": "7️⃣",
            "8": "8️⃣",
            "9": "9️⃣",
            "10": "🔟",
            "11": "🇦",
            "12": "🇧",
            "13": "🇨",
            "14": "🇩",
            "15": "🇪",
            "16": "🇫",
            "17": "🇬",
            "18": "🇭",
            "19": "🇮",
            "20": "🇯",
            "21": "🇰",
            "22": "🇱",
            "23": "🇲",
            "24": "🇳",
            "25": "🇴",
            "26": "🇵",
            "27": "🇶",
            "28": "🇷",
            "29": "🇸",
            "30": "🇹",
            "31": "🇺",
            "32": "🇻",
            "33": "🇼",
            "34": "🇽",
            "35": "🇾",
            "36": "🇿",
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
            "unknown": "❓",
            "status": "⏱️",
            f"{statics.KEY_STATUS}_online": "🟢",
            f"{statics.KEY_STATUS}_offline": "🔴",
            "current_streams": "🌊",
            "current_transcodes": "💦",
            "local_bandwidth": "🏠",
            "remote_bandwidth": "🌐",
            "total_bandwidth": "📶",
        }

    @property
    def stream_number_emojis(self) -> List[str]:
        number_emojis = []
        for i in range(1, max_controllable_stream_count_supported() + 1):
            number_emojis.append(self.emoji_from_stream_number(i))
        return number_emojis

    def stream_number_from_emoji(self, emoji: PartialEmoji) -> Union[int, None]:
        # If using the Tauticord custom emojis, name corresponds to the stream number (e.g. tc_1 is 1, tc_2 is 2, etc.)
        if emoji.name.startswith(self._emoji_prefix):
            number = emoji.name.replace(f"{self._emoji_prefix}_", "")
            return int(number)
        # Not using the Tauticord custom emojis, so we need to check the emoji itself
        for num, e in self._emojis.items():
            if e == str(emoji):
                return int(num)
        return None

    def emoji_from_stream_number(self, number: int) -> str:
        number_str = str(number)
        if number_str in self._emojis:
            return self._emojis[number_str]
        else:
            return self._emojis["unknown"]

    def valid_emoji(self, emoji) -> bool:
        return str(emoji) in self._emojis

    def valid_emoji_for_stream_number(self, emoji, number: int) -> bool:
        return str(emoji) == self.emoji_from_stream_number(number)

    async def load_emojis(self, source_folder: str, client: discord.Client, guild_id: str) -> None:
        # Upload PNG emojis from the source folder
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
                self._emojis[str(name)] = f"<:{name_with_prefix}:{emoji.id}>"
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
