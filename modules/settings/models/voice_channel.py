from modules.settings.models.base import BaseConfig
from modules.utils import strip_phantom_space


class VoiceChannel(BaseConfig):
    name: str
    enable: bool
    emoji: str
    channel_id: int = 0

    @property
    def prefix(self) -> str:
        emoji = strip_phantom_space(string=self.emoji)
        prefix = f"{emoji} {self.name}"
        return prefix.strip()  # Remove any spaces provided to override default name/emoji

    @property
    def channel_id_set(self) -> bool:
        return self.channel_id != 0

    def build_channel_name(self, value) -> str:
        prefix = self.prefix
        if not prefix:
            return value
        return f"{self.prefix}: {value}"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "enable": self.enable,
            "emoji": self.emoji,
            "channel_id": self.channel_id
        }


class RecentlyAddedVoiceChannel(VoiceChannel):
    hours: int = 24

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "enable": self.enable,
            "emoji": self.emoji,
            "channel_id": self.channel_id,
            "hours": self.hours
        }


class LibraryVoiceChannels(BaseConfig):
    movie: VoiceChannel
    album: VoiceChannel
    artist: VoiceChannel
    episode: VoiceChannel
    series: VoiceChannel
    track: VoiceChannel
    recently_added: RecentlyAddedVoiceChannel

    @property
    def _channels(self) -> list[VoiceChannel]:
        return [self.movie, self.album, self.artist, self.episode, self.series, self.track, self.recently_added]

    @property
    def enabled_channels(self) -> list[VoiceChannel]:
        return [channel for channel in self._channels if channel.enable]

    def as_dict(self) -> dict:
        return {
            "movie": self.movie.as_dict(),
            "album": self.album.as_dict(),
            "artist": self.artist.as_dict(),
            "episode": self.episode.as_dict(),
            "series": self.series.as_dict(),
            "track": self.track.as_dict(),
            "recently_added": self.recently_added.as_dict()
        }
