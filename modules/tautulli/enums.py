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


class StatMetricType(enum.Enum):
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


class StatChartType(enum.Enum):
    DAILY_BY_MEDIA_TYPE = 'daily_play_count'
    # DAILY_BY_STREAM_TYPE = 'daily_by_stream_type'
    # DAILY_CONCURRENT_BY_STREAM_TYPE = 'daily_concurrent_by_stream_type'
    BY_HOUR_OF_DAY = 'play_count_by_hourofday'
    BY_DAY_OF_WEEK = 'play_count_by_dayofweek'
    BY_MONTH = 'play_count_by_month'
    BY_TOP_10_PLATFORMS = 'top_10_platforms'
    BY_TOP_10_USERS = 'top_10_users'
    # BY_SOURCE_RESOLUTION = 'by_source_resolution'
    # BY_STREAM_RESOLUTION = 'by_stream_resolution'
    # BY_PLATFORM_AND_STREAM_TYPE = 'by_platform_and_stream_type'
    # BY_USERS_AND_STREAM_TYPE = 'by_users_and_stream_type'


class StatChartColors(enum.Enum):
    BLACK = "#000000"
    WHITE = "#FFFFFF"
    MUSIC = '#F06464'
    MOVIES = WHITE
    TV = '#E5A00D'
    BACKGROUND = "#333333"
    TEXT = "#A6A6A6"
    GRIDLINES = "#D8D5D0"
