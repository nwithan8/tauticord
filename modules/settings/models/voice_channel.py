from modules.settings.models.base import BaseConfig


class VoiceChannel(BaseConfig):
    name: str
    enable: bool
    emoji: str
    channel_id: int = 0

    @property
    def prefix(self) -> str:
        return f"{self.emoji} {self.name}"

    @property
    def channel_id_set(self) -> bool:
        return self.channel_id != 0

    def build_channel_name(self, value) -> str:
        return f"{self.prefix}: {value}"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "enable": self.enable,
            "emoji": self.emoji,
            "channel_id": self.channel_id
        }


class LibraryVoiceChannels(BaseConfig):
    movie: VoiceChannel
    album: VoiceChannel
    artist: VoiceChannel
    episode: VoiceChannel
    series: VoiceChannel
    track: VoiceChannel

    @property
    def _channels(self) -> list[VoiceChannel]:
        return [self.movie, self.album, self.artist, self.episode, self.series, self.track]

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
            "track": self.track.as_dict()
        }
