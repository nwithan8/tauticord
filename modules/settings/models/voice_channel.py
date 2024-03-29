from modules.settings.models.base import BaseConfig


class VoiceChannel(BaseConfig):
    name: str
    enable: bool
    emoji: str
    use_emojis: bool = False
    channel_id: int = 0

    def build_channel_name(self, value) -> str:
        name = self.name
        if self.use_emojis:
            name = f"{self.emoji} {name}"

        return f"{name}: {value}"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "enable": self.enable,
            "emoji": self.emoji,
            "use_emojis": self.use_emojis,
            "channel_id": self.channel_id
        }


class LibraryVoiceChannels(BaseConfig):
    album: VoiceChannel
    artist: VoiceChannel
    episode: VoiceChannel
    series: VoiceChannel
    track: VoiceChannel

    @property
    def _channels(self) -> list[VoiceChannel]:
        return [self.album, self.artist, self.episode, self.series, self.track]

    @property
    def enabled_channels(self) -> list[VoiceChannel]:
        return [channel for channel in self._channels if channel.enable]

    def as_dict(self) -> dict:
        return {
            "album": self.album.as_dict(),
            "artist": self.artist.as_dict(),
            "episode": self.episode.as_dict(),
            "series": self.series.as_dict(),
            "track": self.track.as_dict()
        }
