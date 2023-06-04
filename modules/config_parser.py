import json
import os
from typing import List, Dict, Any

import confuse
import yaml

import modules.logs as logging
from modules import statics
from modules.text_manager import TextManager


def _extract_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ["true", "yes", "1", "t"]:
        return True
    elif value.lower() in ["false", "no", "0", "f"]:
        return False
    else:
        raise ValueError("Not a boolean: {}".format(value))


class ConfigSection:
    def __init__(self, section_key: str, data, parent_key: str = None, pull_from_env: bool = True):
        self.section_key = section_key
        self.data = data
        self.pull_from_env = pull_from_env
        try:
            self.data = data[self.section_key]
        except confuse.NotFoundError:
            pass
        self._parent_key = parent_key

    @property
    def full_key(self):
        if self._parent_key is None:
            return self.section_key
        return f"{self._parent_key}_{self.section_key}".upper()

    def _get_value(self, key: str, default=None, env_name_override: str = None):
        if self.pull_from_env:
            env_name = env_name_override or self.full_key
            return os.getenv(env_name, default)
        try:
            return self.data[key].get()
        except confuse.NotFoundError:
            return default

    def _get_subsection(self, key: str, default=None):
        try:
            return ConfigSection(section_key=key, parent_key=self.full_key, data=self.data,
                                 pull_from_env=self.pull_from_env)
        except confuse.NotFoundError:
            return default


class TautulliConfig(ConfigSection):
    def __init__(self, data, pull_from_env: bool = True):
        super().__init__(section_key="Tautulli", data=data, pull_from_env=pull_from_env)

    @property
    def _connection(self) -> ConfigSection:
        return self._get_subsection(key="Connection")

    @property
    def api_key(self) -> str:
        return self._connection._get_value(key="APIKey", env_name_override="TC_TAUTULLI_KEY")

    @property
    def url(self) -> str:
        return self._connection._get_value(key="URL", env_name_override="TC_TAUTULLI_URL")

    @property
    def _customization(self) -> ConfigSection:
        return self._get_subsection(key="Customization")

    @property
    def has_plex_pass(self) -> bool:
        value = self._customization._get_value(key="PlexPass", env_name_override="TC_PLEX_PASS",
                                               default=False)
        return _extract_bool(value)

    @property
    def refresh_interval(self) -> int:
        value = self._customization._get_value(key='RefreshSeconds', default=15,
                                               env_name_override="TC_REFRESH_SECONDS")
        return int(value)

    @property
    def server_name(self) -> str:
        return self._customization._get_value(key='ServerName', default="Plex",
                                              env_name_override="TC_SERVER_NAME")

    @property
    def terminate_message(self) -> str:
        return self._customization._get_value(key='TerminateMessage', default="Your stream has ended.",
                                              env_name_override="TC_TERMINATE_MESSAGE")

    @property
    def time_settings(self) -> dict:
        timezone = self._customization._get_value(key='ServerTimeZone', default=None, env_name_override="TZ")
        mil_time = self._customization._get_value(key='Use24HourTime', default=False,
                                                  env_name_override="TC_USE_24_HOUR_TIME")
        return {'timezone': timezone,
                'mil_time': mil_time}

    @property
    def _voice_channels(self) -> ConfigSection:
        return self._customization._get_subsection(key="VoiceChannels")

    @property
    def _stats_voice_channels(self) -> ConfigSection:
        return self._voice_channels._get_subsection(key="Stats")

    @property
    def stats_voice_channel_category_name(self) -> str:
        return self._stats_voice_channels._get_value(key="CategoryName", default="Tautulli Stats",
                                                     env_name_override="TC_VC_STATS_CATEGORY_NAME")

    @property
    def display_stream_count(self) -> bool:
        value = self._stats_voice_channels._get_value(key="StreamCount", default=False,
                                                      env_name_override="TC_VC_STREAM_COUNT")
        return _extract_bool(value)

    @property
    def display_transcode_count(self) -> bool:
        value = self._stats_voice_channels._get_value(key="TranscodeCount", default=False,
                                                      env_name_override="TC_VC_TRANSCODE_COUNT")
        return _extract_bool(value)

    @property
    def display_bandwidth(self) -> bool:
        value = self._stats_voice_channels._get_value(key="Bandwidth", default=False,
                                                      env_name_override="TC_VC_BANDWIDTH")
        return _extract_bool(value)

    @property
    def display_local_bandwidth(self) -> bool:
        value = self._stats_voice_channels._get_value(key="LocalBandwidth", default=False,
                                                      env_name_override="TC_VC_LOCAL_BANDWIDTH")
        return _extract_bool(value)

    @property
    def display_remote_bandwidth(self) -> bool:
        value = self._stats_voice_channels._get_value(key="RemoteBandwidth", default=False,
                                                      env_name_override="TC_VC_REMOTE_BANDWIDTH")
        return _extract_bool(value)

    @property
    def display_plex_status(self) -> bool:
        value = self._stats_voice_channels._get_value(key="PlexStatus", default=False,
                                                      env_name_override="TC_VC_PLEX_STATUS")
        return _extract_bool(value)

    @property
    def _libraries_voice_channels(self) -> ConfigSection:
        return self._voice_channels._get_subsection(key="Libraries")

    @property
    def libraries_voice_channel_category_name(self) -> str:
        return self._libraries_voice_channels._get_value(key="CategoryName", default="Tautulli Libraries",
                                                         env_name_override="TC_VC_LIBRARIES_CATEGORY_NAME")

    @property
    def display_library_stats(self) -> bool:
        value = self._libraries_voice_channels._get_value(key="Enable", default=False,
                                                          env_name_override="TC_VC_LIBRARY_STATS")
        return _extract_bool(value)

    @property
    def library_refresh_interval(self) -> int:
        value = self._libraries_voice_channels._get_value(key="LibraryRefreshSeconds", default=3600,
                                                          env_name_override="TC_VC_LIBRARY_REFRESH_SECONDS")
        return int(value)

    @property
    def library_names(self) -> List[str]:
        names = self._libraries_voice_channels._get_value(key="LibraryNames", default=[],
                                                          env_name_override="TC_VC_LIBRARY_NAMES")
        if isinstance(names, str):
            return names.split(",")
        return names

    @property
    def show_tv_series_count(self) -> bool:
        value = self._libraries_voice_channels._get_value(key="TVSeriesCount", default=True,
                                                          env_name_override="TC_VC_TV_SERIES_COUNT")
        return _extract_bool(value)

    @property
    def show_tv_episode_count(self) -> bool:
        value = self._libraries_voice_channels._get_value(key="TVEpisodeCount", default=True,
                                                          env_name_override="TC_VC_TV_EPISODE_COUNT")
        return _extract_bool(value)

    @property
    def show_music_artist_count(self) -> bool:
        value = self._libraries_voice_channels._get_value(key="MusicArtistCount", default=True,
                                                          env_name_override="TC_VC_MUSIC_ARTIST_COUNT")
        return _extract_bool(value)

    @property
    def show_music_track_count(self) -> bool:
        value = self._libraries_voice_channels._get_value(key="MusicTrackCount", default=True,
                                                          env_name_override="TC_VC_MUSIC_TRACK_COUNT")
        return _extract_bool(value)

    @property
    def voice_channel_settings(self) -> Dict[str, Any]:
        return {
            statics.KEY_STATS_CATEGORY_NAME: self.stats_voice_channel_category_name,
            statics.KEY_COUNT: self.display_stream_count,
            statics.KEY_TRANSCODE_COUNT: self.display_transcode_count,
            statics.KEY_BANDWIDTH: self.display_bandwidth,
            statics.KEY_LAN_BANDWIDTH: self.display_local_bandwidth,
            statics.KEY_REMOTE_BANDWIDTH: self.display_remote_bandwidth,
            statics.KEY_STATS: self.display_library_stats,
            statics.KEY_PLEX_STATUS: self.display_plex_status,
            statics.KEY_REFRESH_TIME: self.library_refresh_interval,
            statics.KEY_LIBRARIES_CATEGORY_NAME: self.libraries_voice_channel_category_name,
            statics.KEY_LIBRARIES: self.library_names,
            statics.KEY_SHOW_TV_EPISODES: self.show_tv_episode_count,
            statics.KEY_SHOW_TV_SERIES: self.show_tv_series_count,
            statics.KEY_SHOW_MUSIC_ARTISTS: self.show_music_artist_count,
            statics.KEY_SHOW_MUSIC_TRACKS: self.show_music_track_count
        }

    @property
    def any_live_stats_channels_enabled(self) -> bool:
        keys = [statics.KEY_COUNT, statics.KEY_TRANSCODE_COUNT, statics.KEY_BANDWIDTH,
                statics.KEY_LAN_BANDWIDTH, statics.KEY_REMOTE_BANDWIDTH, statics.KEY_PLEX_STATUS]
        return any([self.voice_channel_settings.get(key, False) for key in keys])

    @property
    def any_library_stats_channels_enabled(self) -> bool:
        keys = [statics.KEY_STATS]
        return any([self.voice_channel_settings.get(key, False) for key in keys])

    @property
    def _anonymize_rules(self) -> ConfigSection:
        return self._customization._get_subsection(key="Anonymize")

    @property
    def _anonymize_hide_usernames(self) -> bool:
        value = self._anonymize_rules._get_value(key="HideUsernames", default=False,
                                                 env_name_override="TC_HIDE_USERNAMES")
        return _extract_bool(value)

    @property
    def _anonymize_hide_platforms(self) -> bool:
        value = self._anonymize_rules._get_value(key="HidePlatforms", default=False,
                                                 env_name_override="TC_HIDE_PLATFORMS")
        return _extract_bool(value)

    @property
    def _anonymize_hide_player_names(self) -> str:
        return self._anonymize_rules._get_value(key="HidePlayerNames", default=False,
                                                env_name_override="TC_HIDE_PLAYER_NAMES")

    @property
    def _anonymize_hide_quality(self) -> bool:
        value = self._anonymize_rules._get_value(key="HideQuality", default=False,
                                                 env_name_override="TC_HIDE_QUALITY")
        return _extract_bool(value)

    @property
    def _anonymize_hide_bandwidth(self) -> bool:
        value = self._anonymize_rules._get_value(key="HideBandwidth", default=False,
                                                 env_name_override="TC_HIDE_BANDWIDTH")
        return _extract_bool(value)

    @property
    def _anonymize_hide_transcode_decision(self) -> bool:
        value = self._anonymize_rules._get_value(key="HideTranscode", default=False,
                                                 env_name_override="TC_HIDE_TRANSCODE")
        return _extract_bool(value)

    @property
    def _anonymize_hide_progress(self) -> bool:
        value = self._anonymize_rules._get_value(key="HideProgress", default=False,
                                                 env_name_override="TC_HIDE_PROGRESS")
        return _extract_bool(value)

    @property
    def _anonymize_hide_eta(self) -> bool:
        value = self._anonymize_rules._get_value(key="HideETA", default=False,
                                                 env_name_override="TC_HIDE_ETA")
        return _extract_bool(value)

    @property
    def _performance_voice_channel_settings(self) -> ConfigSection:
        return self._voice_channels._get_subsection(key="Performance")

    @property
    def _performance_voice_channel_name(self) -> str:
        return self._performance_voice_channel_settings._get_value(key="CategoryName", default="Performance",
                                                                   env_name_override="TC_VC_PERFORMANCE_CATEGORY_NAME")

    @property
    def text_manager(self) -> TextManager:
        anonymous_rules = {
            statics.KEY_HIDE_USERNAMES: self._anonymize_hide_usernames,
            statics.KEY_HIDE_PLAYER_NAMES: self._anonymize_hide_player_names,
            statics.KEY_HIDE_PLATFORMS: self._anonymize_hide_platforms,
            statics.KEY_HIDE_QUALITY: self._anonymize_hide_quality,
            statics.KEY_HIDE_BANDWIDTH: self._anonymize_hide_bandwidth,
            statics.KEY_HIDE_TRANSCODING: self._anonymize_hide_transcode_decision,
            statics.KEY_HIDE_PROGRESS: self._anonymize_hide_progress,
            statics.KEY_HIDE_ETA: self._anonymize_hide_eta,
        }
        return TextManager(anon_rules=anonymous_rules)


class DiscordConfig(ConfigSection):
    def __init__(self, data, pull_from_env: bool = True):
        super().__init__(section_key="Discord", data=data, pull_from_env=pull_from_env)

    @property
    def _connection(self) -> ConfigSection:
        return self._get_subsection(key="Connection")

    @property
    def bot_token(self) -> str:
        return self._connection._get_value(key="BotToken", env_name_override="TC_DISCORD_BOT_TOKEN")

    @property
    def server_id(self) -> str:
        value = self._connection._get_value(key="ServerID", env_name_override="TC_DISCORD_SERVER_ID")
        return str(value)

    @property
    def admin_ids(self) -> List[str]:
        ids = self._connection._get_value(key="AdminIDs", default=[], env_name_override="TC_DISCORD_ADMIN_IDS")
        if isinstance(ids, str):
            return [str(i) for i in ids.split(",")]
        return [str(i) for i in ids]

    @property
    def channel_name(self) -> str:
        return self._connection._get_value(key="ChannelName", default="tauticord",
                                           env_name_override="TC_DISCORD_CHANNEL_NAME")

    @property
    def _customization(self) -> ConfigSection:
        return self._get_subsection(key="Customization")

    @property
    def has_discord_nitro(self) -> bool:
        value = self._customization._get_value(key="Nitro", env_name_override="TC_DISCORD_NITRO",
                                               default=False)
        return _extract_bool(value)


class ExtrasConfig(ConfigSection):
    def __init__(self, data, pull_from_env: bool = True):
        super().__init__(section_key="Extras", data=data, pull_from_env=pull_from_env)

    @property
    def allow_analytics(self) -> bool:
        value = self._get_value(key="Analytics", default=True,
                                env_name_override="TC_ALLOW_ANALYTICS")
        return _extract_bool(value)

    @property
    def _performance(self) -> ConfigSection:
        return self._get_subsection(key="Performance")

    @property
    def _performance_monitor_cpu(self) -> bool:
        value = self._performance._get_value(key="CPU", default=False,
                                             env_name_override="TC_MONITOR_CPU")
        return _extract_bool(value)

    @property
    def _performance_monitor_memory(self) -> bool:
        value = self._performance._get_value(key="Memory", default=False,
                                             env_name_override="TC_MONITOR_MEMORY")
        return _extract_bool(value)


class Config:
    def __init__(self, app_name: str, config_path: str, fallback_to_env: bool = True):
        self.config = confuse.Configuration(app_name)
        self.pull_from_env = False
        # noinspection PyBroadException
        try:
            self.config.set_file(filename=config_path)
            logging.debug(f"Loaded config from {config_path}")
        except Exception:  # pylint: disable=broad-except # not sure what confuse will throw
            if not fallback_to_env:
                raise FileNotFoundError(f"Config file not found: {config_path}")
            self.pull_from_env = True
            logging.debug(f"Config file not found: {config_path}, falling back to environment variables")

        self.tautulli = TautulliConfig(self.config, self.pull_from_env)
        self.discord = DiscordConfig(self.config, self.pull_from_env)
        self.extras = ExtrasConfig(self.config, self.pull_from_env)
        self.performance = {
            statics.KEY_PERFORMANCE_CATEGORY_NAME: self.tautulli._performance_voice_channel_name,
            statics.KEY_PERFORMANCE_MONITOR_CPU: self.extras._performance_monitor_cpu,
            statics.KEY_PERFORMANCE_MONITOR_MEMORY: self.extras._performance_monitor_memory,
        }

    def __repr__(self) -> str:
        raw_yaml_data = self.config.dump()
        json_data = yaml.load(raw_yaml_data, Loader=yaml.FullLoader)
        return json.dumps(json_data, indent=4)
