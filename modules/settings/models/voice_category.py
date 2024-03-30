from modules.settings.models.base import BaseConfig

from modules.settings.models.libraries import CombinedLibrary, Library
from modules.settings.models.voice_channel import VoiceChannel


class VoiceCategory(BaseConfig):
    category_name: str
    enable: bool

    def as_dict(self) -> dict:
        raise NotImplementedError

    def channel_order(self) -> dict:
        raise NotImplementedError


class ActivityStats(VoiceCategory):
    bandwidth: VoiceChannel
    local_bandwidth: VoiceChannel
    remote_bandwidth: VoiceChannel
    stream_count: VoiceChannel
    transcode_count: VoiceChannel
    plex_availability: VoiceChannel

    def as_dict(self) -> dict:
        return {
            "category_name": self.category_name,
            "enable": self.enable,
            "bandwidth": self.bandwidth.as_dict(),
            "local_bandwidth": self.local_bandwidth.as_dict(),
            "remote_bandwidth": self.remote_bandwidth.as_dict(),
            "stream_count": self.stream_count.as_dict(),
            "transcode_count": self.transcode_count.as_dict(),
            "plex_availability": self.plex_availability.as_dict()
        }


class LibraryStats(VoiceCategory):
    libraries: list[Library]
    combined_libraries: list[CombinedLibrary]
    refresh_interval_seconds: int

    def as_dict(self) -> dict:
        return {
            "category_name": self.category_name,
            "enable": self.enable,
            "libraries": [library.as_dict() for library in self.libraries],
            "combined_libraries": [library.as_dict() for library in self.combined_libraries],
            "refresh_interval_seconds": self.refresh_interval_seconds
        }


class PerformanceStats(VoiceCategory):
    cpu: VoiceChannel
    memory: VoiceChannel
    disk: VoiceChannel
    user_count: VoiceChannel

    def as_dict(self) -> dict:
        return {
            "category_name": self.category_name,
            "enable": self.enable,
            "cpu": self.cpu.as_dict(),
            "memory": self.memory.as_dict(),
            "disk": self.disk.as_dict(),
            "user_count": self.user_count.as_dict()
        }
