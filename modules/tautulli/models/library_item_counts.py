from typing import Optional

from pydantic import BaseModel

from modules.tautulli.enums import LibraryType


class LibraryItemCounts(BaseModel):
    library_name: str
    library_type: LibraryType
    movies: Optional[int] = None
    albums: Optional[int] = None
    artists: Optional[int] = None
    episodes: Optional[int] = None
    seasons: Optional[int] = None
    series: Optional[int] = None
    tracks: Optional[int] = None
