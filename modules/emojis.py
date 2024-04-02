import enum
from pathlib import Path
from typing import Optional, Union, List

import discord
from discord import Emoji, PartialEmoji
from pydantic import BaseModel

import modules.logs as logging
from modules import statics


class EmojiFile(BaseModel):
    path: str

    @property
    def name(self) -> str:
        return Path(self.path).stem

    @property
    def name_with_prefix(self) -> str:
        return f"{statics.EMOJI_PREFIX}_{self.name}"


async def upload_new_emoji(emoji_file: EmojiFile, client: discord.Client, guild_id: int) -> Union[discord.Emoji, None]:
    guild = client.get_guild(guild_id)  # stupid positional-only parameters

    # Upload the new emoji
    try:
        logging.info(f"Uploading emoji '{emoji_file.name_with_prefix}' to server")
        with open(emoji_file.path, 'rb') as f:
            image_bytes: bytes = f.read()
            return await guild.create_custom_emoji(name=emoji_file.name_with_prefix, image=image_bytes,
                                                   reason="Tauticord emoji upload")
    except Exception as e:
        logging.error(
            f"Failed to upload emoji '{emoji_file.name_with_prefix}' to server: {e}. Will use default emoji instead.")
        return None


async def collect_guild_emojis(client: discord.Client, guild_id: int) -> tuple[Emoji, ...]:
    guild = client.get_guild(guild_id)  # stupid positional-only parameters

    return guild.emojis


async def get_corresponding_emoji_from_server(emoji_file: EmojiFile, client: discord.Client, guild_id: int) -> Union[
    Emoji, None]:
    existing_emojis = await collect_guild_emojis(client=client, guild_id=guild_id)

    for emoji in existing_emojis:
        if emoji.name == emoji_file.name_with_prefix:
            return emoji

    return None


def max_controllable_stream_count_supported(max_streams_override: Optional[int] = None) -> int:
    return max_streams_override or statics.MAX_STREAM_COUNT


class Emoji(enum.Enum):
    Number1 = "1⃣"
    Number2 = "2⃣"
    Number3 = "3⃣"
    Number4 = "4⃣"
    Number5 = "5⃣"
    Number6 = "6⃣"
    Number7 = "7⃣"
    Number8 = "8⃣"
    Number9 = "9⃣"
    Number10 = "10⃣"
    LetterA = "A⃣"
    LetterB = "B⃣"
    LetterC = "C⃣"
    LetterD = "D⃣"
    LetterE = "E⃣"
    LetterF = "F⃣"
    LetterG = "G⃣"
    LetterH = "H⃣"
    LetterI = "I⃣"
    LetterJ = "J⃣"
    LetterK = "K⃣"
    LetterL = "L⃣"
    LetterM = "M⃣"
    LetterN = "N⃣"
    LetterO = "O⃣"
    LetterP = "P⃣"
    LetterQ = "Q⃣"
    LetterR = "R⃣"
    LetterS = "S⃣"
    LetterT = "T⃣"
    LetterU = "U⃣"
    LetterV = "V⃣"
    LetterW = "W⃣"
    LetterX = "X⃣"
    LetterY = "Y⃣"
    LetterZ = "Z⃣"
    Bandwidth = "📶"
    LocalBandwidth = "🏠"
    RemoteBandwidth = "🌐"
    Buffering = "⏳"
    Clip = "🎞"
    Episode = "🧩"
    Error = "⚠"
    Home = "🏠"
    Live = "📡"
    Movie = "🎥"
    Paused = "⏸"
    Person = "👤"
    Photo = "🖼"
    Playing = "▶"
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
        if emoji.name.startswith(statics.EMOJI_PREFIX):
            number = emoji.name.replace(f"{statics.EMOJI_PREFIX}_", "")
            return int(number)

        # Not using the Tauticord custom emojis, so we need to check the emoji itself
        for num, e in self._emoji_aliases.items():
            if e == str(emoji):
                return int(num)
        return None

    def is_valid_emoji_for_stream_number(self, emoji, number: int) -> bool:
        return str(emoji) == self.emoji_from_stream_number(number)

    def custom_emoji_files(self) -> List[EmojiFile]:
        emoji_files = []
        for file in Path(statics.CUSTOM_EMOJIS_FOLDER).glob("*.png"):
            emoji_files.append(
                EmojiFile(path=str(file))
            )
        return emoji_files

    async def get_un_uploaded_emoji_files(self, client: discord.Client, guild_id: int) -> List[EmojiFile]:
        emoji_files = self.custom_emoji_files()
        uploaded_emojis = await collect_guild_emojis(client=client, guild_id=guild_id)
        uploaded_emojis_names = [emoji.name for emoji in uploaded_emojis]

        return [emoji_file for emoji_file in emoji_files if emoji_file.name_with_prefix not in uploaded_emojis_names]

    async def load_custom_emojis(self, client: discord.Client, guild_id: int) -> None:
        # Upload PNG emojis from the source folder
        for emoji_file in self.custom_emoji_files():
            await self.upload_and_cache_emoji(emoji_file=emoji_file, client=client, guild_id=guild_id)

    async def upload_and_cache_emoji(self, emoji_file: EmojiFile, client: discord.Client, guild_id: int) -> None:
        emoji = await get_corresponding_emoji_from_server(emoji_file=emoji_file, client=client,
                                                          guild_id=guild_id)
        if not emoji:
            emoji = await upload_new_emoji(emoji_file=emoji_file, client=client, guild_id=guild_id)

            if not emoji:  # Emoji upload failed
                return  # Keep the default emoji

        # Store the emoji in the cache
        self._emoji_aliases[str(emoji_file.name)] = f"<:{emoji.name}:{emoji.id}>"
