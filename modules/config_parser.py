import json
import os
from typing import List

import confuse
import yaml

from modules import statics


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
    def voice_channel_settings(self):
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
            statics.KEY_LIBRARIES: self.library_names
        }


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
    def server_id(self) -> int:
        value = self._connection._get_value(key="ServerID", env_name_override="TC_DISCORD_SERVER_ID")
        return int(value)

    @property
    def admin_ids(self) -> List[int]:
        ids = self._connection._get_value(key="AdminIDs", default=[], env_name_override="TC_DISCORD_ADMIN_IDS")
        if isinstance(ids, str):
            return [int(i) for i in ids.split(",")]
        return [int(i) for i in ids]

    @property
    def channel_name(self) -> str:
        return self._connection._get_value(key="ChannelName", env_name_override="TC_DISCORD_CHANNEL_NAME")

    @property
    def _customization(self) -> ConfigSection:
        return self._get_subsection(key="Customization")

    @property
    def use_embeds(self) -> bool:
        value = self._customization._get_value(key="UseEmbeds", default=False, env_name_override="TC_USE_EMBEDS")
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
    def log_level(self) -> str:
        return self._get_value(key="LogLevel", default="INFO",
                               env_name_override="TC_LOG_LEVEL")


class Config:
    def __init__(self, app_name: str, config_path: str, fallback_to_env: bool = True):
        self.config = confuse.Configuration(app_name)
        self.pull_from_env = False
        # noinspection PyBroadException
        try:
            self.config.set_file(filename=config_path)
        except Exception:  # pylint: disable=broad-except # not sure what confuse will throw
            if not fallback_to_env:
                raise FileNotFoundError(f"Config file not found: {config_path}")
            self.pull_from_env = True

        self.tautulli = TautulliConfig(self.config, self.pull_from_env)
        self.discord = DiscordConfig(self.config, self.pull_from_env)
        self.extras = ExtrasConfig(self.config, self.pull_from_env)
        self.log_level = self.extras.log_level

    def __repr__(self) -> str:
        raw_yaml_data = self.config.dump()
        json_data = yaml.load(raw_yaml_data, Loader=yaml.FullLoader)
        return json.dumps(json_data, indent=4)
