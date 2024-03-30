import enum


class LibraryType(enum.Enum):
    MOVIE = 'movie'
    SHOW = 'show'
    MUSIC = 'artist'

    @staticmethod
    def from_str(value: str) -> 'LibraryType':
        if value == 'movie':
            return LibraryType.MOVIE
        if value == 'show':
            return LibraryType.SHOW
        if value == 'artist':
            return LibraryType.MUSIC
        raise ValueError(f"Invalid library type: {value}")


class HomeStatMetricType(enum.Enum):
    PLAYS = 'plays'
    DURATION = 'duration'


class HomeStatType(enum.Enum):
    TOP_MOVIES = 'top_movies'
    POPULAR_MOVIES = 'popular_movies'
    TOP_TV = 'top_tv'
    POPULAR_TV = 'popular_tv'
    TOP_MUSIC = 'top_music'
    POPULAR_MUSIC = 'popular_music'
    TOP_LIBRARIES = 'top_libraries'
    TOP_USERS = 'top_users'
    TOP_PLATFORMS = 'top_platforms'
    LAST_WATCHED = 'last_watched'
    MOST_CONCURRENT = 'most_concurrent'
