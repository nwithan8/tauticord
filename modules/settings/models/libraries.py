from modules.settings.models.base import BaseConfig

from modules.settings.models.voice_channel import LibraryVoiceChannels


class BaseLibrary(BaseConfig):
    name: str
    voice_channels: LibraryVoiceChannels

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "voice_channels": self.voice_channels.as_dict()
        }


class Library(BaseLibrary):
    alternate_name: str

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "alternate_name": self.alternate_name,
            "voice_channels": self.voice_channels.as_dict()
        }


class CombinedLibrary(BaseLibrary):
    libraries: list[str]

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "libraries": self.libraries,
            "voice_channels": self.voice_channels.as_dict()
        }
