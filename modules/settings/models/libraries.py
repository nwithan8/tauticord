from typing import Optional, Union

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
    id: Optional[int]

    @property
    def library_id(self) -> Union[int, None]:
        if not self.id:
            return None

        return self.id if self.id > 0 else None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "alternate_name": self.alternate_name,
            "voice_channels": self.voice_channels.as_dict()
        }


class CombinedLibrarySubLibrary(BaseConfig):
    name: str
    id: int

    @property
    def library_id(self) -> Union[int, None]:
        if not self.id:
            return None
        return self.id if self.id > 0 else None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id
        }


class CombinedLibrary(BaseLibrary):
    libraries: list[CombinedLibrarySubLibrary]

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "libraries": [library.as_dict() for library in self.libraries],
            "voice_channels": self.voice_channels.as_dict()
        }
