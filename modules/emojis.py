import enum
from pathlib import Path
from typing import Optional, Union, List

import discord
from discord import Emoji, PartialEmoji

import modules.logs as logging
from modules import statics


async def upload_new_emoji(file: str, name: str, client: discord.Client, guild_id: int) -> Union[discord.Emoji, None]:
    guild = client.get_guild(guild_id)  # stupid positional-only parameters

    # Upload the new emoji
    try:
        with open(file, 'rb') as f:
            image_bytes: bytes = f.read()
            return await guild.create_custom_emoji(name=name, image=image_bytes, reason="Tauticord emoji upload")
    except Exception as e:
        logging.error(f"Failed to upload emoji {name} to server: {e}. Will use default emoji instead.")
        return None


async def collect_guild_emojis(client: discord.Client, guild_id: int) -> tuple[Emoji, ...]:
    guild = client.get_guild(guild_id)  # stupid positional-only parameters

    return guild.emojis


def max_controllable_stream_count_supported(max_streams_override: Optional[int] = None) -> int:
    return max_streams_override or statics.MAX_STREAM_COUNT


class Emoji(enum.Enum):
    Number1 = "1️⃣"
    Number2 = "2️⃣"
    Number3 = "3️⃣"
    Number4 = "4️⃣"
    Number5 = "5️⃣"
    Number6 = "6️⃣"
    Number7 = "7️⃣"
    Number8 = "8️⃣"
    Number9 = "9️⃣"
    Number10 = "🔟"
    LetterA = "🇦"
    LetterB = "🇧"
    LetterC = "🇨"
    LetterD = "🇩"
    LetterE = "🇪"
    LetterF = "🇫"
    LetterG = "🇬"
    LetterH = "🇭"
    LetterI = "🇮"
    LetterJ = "🇯"
    LetterK = "🇰"
    LetterL = "🇱"
    LetterM = "🇲"
    LetterN = "🇳"
    LetterO = "🇴"
    LetterP = "🇵"
    LetterQ = "🇶"
    LetterR = "🇷"
    LetterS = "🇸"
    LetterT = "🇹"
    LetterU = "🇺"
    LetterV = "🇻"
    LetterW = "🇼"
    LetterX = "🇽"
    LetterY = "🇾"
    LetterZ = "🇿"
    Bandwidth = "📶"
    LocalBandwidth = "🏠"
    RemoteBandwidth = "🌐"
    Buffering = "⏳"
    Clip = "🎞"
    Episode = "🧩"
    Error = "⚠️"
    Home = "🏠"
    Live = "📡"
    Movie = "🎥"
    Paused = "⏸"
    Person = "👤"
    Photo = "🖼"
    Playing = "▶️"
    Stopped = "⏹"
    Device = "📱"
    Resolution = "🖥"
    Progress = "⏰"
    Series = "📺"
    Artist = "🎤"
    Album = "📀"
    Track = "🎵"
    Unknown = "❓"
    Status = "🔔"
    Online = "✅"
    Offline = "❌"
    Stream = "🌊"
    Transcode = "💦"
    CPU = "🧠"
    Memory = "🐏"
    Disk = "💾"


class EmojiManager:
    def __init__(self) -> None:
        self._emoji_prefix = "tc"

        # Additional emojis added/updated in the cache will be strings, so it all has to be strings
        self._emoji_aliases = {
            "1": Emoji.Number1.value,
            "2": Emoji.Number2.value,
            "3": Emoji.Number3.value,
            "4": Emoji.Number4.value,
            "5": Emoji.Number5.value,
            "6": Emoji.Number6.value,
            "7": Emoji.Number7.value,
            "8": Emoji.Number8.value,
            "9": Emoji.Number9.value,
            "10": Emoji.Number10.value,
            "11": Emoji.LetterA.value,
            "12": Emoji.LetterB.value,
            "13": Emoji.LetterC.value,
            "14": Emoji.LetterD.value,
            "15": Emoji.LetterE.value,
            "16": Emoji.LetterF.value,
            "17": Emoji.LetterG.value,
            "18": Emoji.LetterH.value,
            "19": Emoji.LetterI.value,
            "20": Emoji.LetterJ.value,
            "21": Emoji.LetterK.value,
            "22": Emoji.LetterL.value,
            "23": Emoji.LetterM.value,
            "24": Emoji.LetterN.value,
            "25": Emoji.LetterO.value,
            "26": Emoji.LetterP.value,
            "27": Emoji.LetterQ.value,
            "28": Emoji.LetterR.value,
            "29": Emoji.LetterS.value,
            "30": Emoji.LetterT.value,
            "31": Emoji.LetterU.value,
            "32": Emoji.LetterV.value,
            "33": Emoji.LetterW.value,
            "34": Emoji.LetterX.value,
            "35": Emoji.LetterY.value,
            "36": Emoji.LetterZ.value,
            "bandwidth": Emoji.Bandwidth.value,
            "buffering": Emoji.Buffering.value,
            "clip": Emoji.Clip.value,
            "episode": Emoji.Episode.value,
            "episodes": Emoji.Episode.value,
            "error": Emoji.Error.value,
            "home": Emoji.Home.value,
            "live": Emoji.Live.value,
            "movie": Emoji.Movie.value,
            "movies": Emoji.Movie.value,
            "paused": Emoji.Paused.value,
            "person": Emoji.Person.value,
            "photo": Emoji.Photo.value,
            "playing": Emoji.Playing.value,
            "stopped": Emoji.Stopped.value,
            "device": Emoji.Device.value,
            "resolution": Emoji.Resolution.value,
            "progress": Emoji.Progress.value,
            "show": Emoji.Series.value,
            "shows": Emoji.Series.value,
            "series": Emoji.Series.value,
            "artist": Emoji.Artist.value,
            "artists": Emoji.Artist.value,
            "album": Emoji.Album.value,
            "albums": Emoji.Album.value,
            "track": Emoji.Track.value,
            "tracks": Emoji.Track.value,
            "unknown": Emoji.Unknown.value,
            "status": Emoji.Status.value,
            "online": Emoji.Online.value,
            "offline": Emoji.Offline.value,
            "stream": Emoji.Stream.value,
            "streams": Emoji.Stream.value,
            "current_streams": Emoji.Stream.value,
            "transcode": Emoji.Transcode.value,
            "transcodes": Emoji.Transcode.value,
            "current_transcodes": Emoji.Transcode.value,
            "local_bandwidth": Emoji.LocalBandwidth.value,
            "remote_bandwidth": Emoji.RemoteBandwidth.value,
            "total_bandwidth": Emoji.Bandwidth.value,
            "cpu": Emoji.CPU.value,
            "memory": Emoji.Memory.value,
            "disk": Emoji.Disk.value,
        }

    def get_emoji(self, key: str) -> str:
        return self._emoji_aliases.get(key, "")  # Return an empty string if the emoji is not found

    def is_valid_emoji(self, emoji) -> bool:
        return str(emoji) in self._emoji_aliases.values()

    @property
    def stream_number_emojis(self) -> List[str]:
        number_emojis = []

        for i in range(1, max_controllable_stream_count_supported() + 1):
            number_emojis.append(self.emoji_from_stream_number(number=i))

        return number_emojis

    def emoji_from_stream_number(self, number: int) -> str:
        number_str = str(number)
        return self._emoji_aliases.get(number_str, "❓")  # Return a question mark if the emoji is not found

    def stream_number_from_emoji(self, emoji: PartialEmoji) -> Union[int, None]:
        # If using the Tauticord custom emojis, name corresponds to the stream number (e.g. tc_1 is 1, tc_2 is 2, etc.)
        if emoji.name.startswith(self._emoji_prefix):
            number = emoji.name.replace(f"{self._emoji_prefix}_", "")
            return int(number)

        # Not using the Tauticord custom emojis, so we need to check the emoji itself
        for num, e in self._emoji_aliases.items():
            if e == str(emoji):
                return int(num)
        return None

    def is_valid_emoji_for_stream_number(self, emoji, number: int) -> bool:
        return str(emoji) == self.emoji_from_stream_number(number)

    async def load_emojis(self, source_folder: str, client: discord.Client, guild_id: int) -> None:
        # Upload PNG emojis from the source folder
        for file in Path(source_folder).glob("*.png"):
            await self.add_new_emoji(file=str(file), client=client, guild_id=guild_id)

    async def add_new_emoji(self, file: str, client: discord.Client, guild_id: int, name: Optional[str] = None) -> None:
        name = name or Path(file).stem
        name_with_prefix = f"{self._emoji_prefix}_{name}"

        # Check if the emoji already exists
        existing_emojis = await collect_guild_emojis(client=client, guild_id=guild_id)
        for emoji in existing_emojis:
            if emoji.name == name_with_prefix:
                # Store the emoji in the cache if it already exists
                self._emoji_aliases[str(name)] = f"<:{name_with_prefix}:{emoji.id}>"
                return

        # Upload the new emoji
        emoji = await upload_new_emoji(file=file, name=name_with_prefix, client=client, guild_id=guild_id)

        if not emoji:  # Emoji upload failed
            return  # Keep the default emoji

        # Store the new emoji in the cache
        self._emoji_aliases[name] = f"<:{name_with_prefix}:{emoji.id}>"
        return
