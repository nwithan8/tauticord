from modules.statics import (
    KEY_SHOW_TV_EPISODES,
    KEY_SHOW_TV_SERIES,
    KEY_SHOW_MUSIC_ARTISTS,
    KEY_SHOW_MUSIC_TRACKS,
)


class LibraryVoiceChannelsVisibilities:
    def __init__(self, settings: dict):
        self.show_tv_episodes = settings.get(KEY_SHOW_TV_EPISODES, False)
        self.show_tv_series = settings.get(KEY_SHOW_TV_SERIES, False)
        self.show_music_artists = settings.get(KEY_SHOW_MUSIC_ARTISTS, False)
        self.show_music_tracks = settings.get(KEY_SHOW_MUSIC_TRACKS, False)
