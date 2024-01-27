import json
import os
from typing import List, Dict, Any

import confuse
import yaml

import modules.logs as logging
from modules import statics, utils
from modules.text_manager import TextManager
from modules.time_manager import TimeManager


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
    def disable_ssl_verification(self) -> bool:
        value = self._connection._get_value(key="UseSelfSignedCert", default=False,
                                            env_name_override="TC_USE_SELF_SIGNED_CERT")
        return _extract_bool(value)

    @property
    def _customization(self) -> ConfigSection:
        return self._get_subsection(key="Customization")

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
    def time_manager(self) -> TimeManager:
        timezone = self._customization._get_value(key='ServerTimeZone', default=None, env_name_override="TZ")
        mil_time = self._customization._get_value(key='Use24HourTime', default=False,
                                                  env_name_override="TC_USE_24_HOUR_TIME")
        return TimeManager(timezone=timezone, military_time=mil_time)

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
    def stream_count_channel_id(self) -> int:
        value = self._stats_voice_channels._get_value(key="StreamCountChannelID", default=0,
                                                      env_name_override="TC_VC_STREAM_COUNT_CHANNEL_ID")
        return int(value)

    @property
    def display_transcode_count(self) -> bool:
        value = self._stats_voice_channels._get_value(key="TranscodeCount", default=False,
                                                      env_name_override="TC_VC_TRANSCODE_COUNT")
        return _extract_bool(value)

    @property
    def transcode_count_channel_id(self) -> int:
        value = self._stats_voice_channels._get_value(key="TranscodeCountChannelID", default=0,
                                                      env_name_override="TC_VC_TRANSCODE_COUNT_CHANNEL_ID")
        return int(value)

    @property
    def display_bandwidth(self) -> bool:
        value = self._stats_voice_channels._get_value(key="Bandwidth", default=False,
                                                      env_name_override="TC_VC_BANDWIDTH")
        return _extract_bool(value)

    @property
    def bandwidth_channel_id(self) -> int:
        value = self._stats_voice_channels._get_value(key="BandwidthChannelID", default=0,
                                                      env_name_override="TC_VC_BANDWIDTH_CHANNEL_ID")
        return int(value)

    @property
    def display_local_bandwidth(self) -> bool:
        value = self._stats_voice_channels._get_value(key="LocalBandwidth", default=False,
                                                      env_name_override="TC_VC_LOCAL_BANDWIDTH")
        return _extract_bool(value)

    @property
    def local_bandwidth_channel_id(self) -> int:
        value = self._stats_voice_channels._get_value(key="LocalBandwidthChannelID", default=0,
                                                      env_name_override="TC_VC_LOCAL_BANDWIDTH_CHANNEL_ID")
        return int(value)

    @property
    def display_remote_bandwidth(self) -> bool:
        value = self._stats_voice_channels._get_value(key="RemoteBandwidth", default=False,
                                                      env_name_override="TC_VC_REMOTE_BANDWIDTH")
        return _extract_bool(value)

    @property
    def remote_bandwidth_channel_id(self) -> int:
        value = self._stats_voice_channels._get_value(key="RemoteBandwidthChannelID", default=0,
                                                      env_name_override="TC_VC_REMOTE_BANDWIDTH_CHANNEL_ID")
        return int(value)

    @property
    def display_plex_status(self) -> bool:
        value = self._stats_voice_channels._get_value(key="PlexStatus", default=False,
                                                      env_name_override="TC_VC_PLEX_STATUS")
        return _extract_bool(value)

    @property
    def plex_status_use_emoji(self) -> bool:
        value = self._stats_voice_channels._get_value(key="PlexStatusUseEmoji", default=False,
                                                      env_name_override="TC_VC_PLEX_STATUS_USE_EMOJI")
        return _extract_bool(value)

    @property
    def plex_status_channel_id(self) -> int:
        value = self._stats_voice_channels._get_value(key="PlexStatusChannelID", default=0,
                                                      env_name_override="TC_VC_PLEX_STATUS_CHANNEL_ID")
        return int(value)

    @property
    def stats_voice_channels_ids(self) -> dict:
        return {
            statics.KEY_STREAM_COUNT_CHANNEL_ID: self.stream_count_channel_id,
            statics.KEY_TRANSCODE_COUNT_CHANNEL_ID: self.transcode_count_channel_id,
            statics.KEY_BANDWIDTH_CHANNEL_ID: self.bandwidth_channel_id,
            statics.KEY_LAN_BANDWIDTH_CHANNEL_ID: self.local_bandwidth_channel_id,
            statics.KEY_REMOTE_BANDWIDTH_CHANNEL_ID: self.remote_bandwidth_channel_id,
            statics.KEY_PLEX_STATUS_CHANNEL_ID: self.plex_status_channel_id
        }

    @property
    def _use_stats_voice_channel_ids(self) -> bool:
        # If any of the stats voice channel IDs are not 0, then we are using them all.
        return any(channel_id != 0 for channel_id in self.stats_voice_channels_ids.values())

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
    def use_emojis_with_library_names(self) -> bool:
        value = self._libraries_voice_channels._get_value(key="UseEmojis", default=True,
                                                          env_name_override="TC_VC_LIBRARY_USE_EMOJIS")
        return _extract_bool(value)

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
            statics.KEY_PLEX_STATUS_USE_EMOJI: self.plex_status_use_emoji,
            statics.KEY_REFRESH_TIME: self.library_refresh_interval,
            statics.KEY_LIBRARIES_CATEGORY_NAME: self.libraries_voice_channel_category_name,
            statics.KEY_LIBRARIES: self.library_names,
            statics.KEY_USE_EMOJIS: self.use_emojis_with_library_names,
            statics.KEY_SHOW_TV_EPISODES: self.show_tv_episode_count,
            statics.KEY_SHOW_TV_SERIES: self.show_tv_series_count,
            statics.KEY_SHOW_MUSIC_ARTISTS: self.show_music_artist_count,
            statics.KEY_SHOW_MUSIC_TRACKS: self.show_music_track_count,
            statics.KEY_STATS_CHANNEL_IDS: self.stats_voice_channels_ids,
            statics.KEY_USE_STATS_CHANNEL_IDS: self._use_stats_voice_channel_ids,
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
    def _use_friendly_names(self) -> str:
        return self._customization._get_value(key='UseFriendlyNames', default=False,
                                              env_name_override="TC_USE_FRIENDLY_NAMES")

    @property
    def thousands_separator(self) -> str:
        return self._customization._get_value(key='ThousandsSeparator', default="",
                                              env_name_override="TC_THOUSANDS_SEPARATOR")

    @property
    def _performance_voice_channel_settings(self) -> ConfigSection:
        return self._voice_channels._get_subsection(key="Performance")

    @property
    def _performance_voice_channel_name(self) -> str:
        return self._performance_voice_channel_settings._get_value(key="CategoryName", default="Performance",
                                                                   env_name_override="TC_VC_PERFORMANCE_CATEGORY_NAME")

    @property
    def text_manager(self) -> TextManager:
        rules = {
            statics.KEY_HIDE_USERNAMES: self._anonymize_hide_usernames,
            statics.KEY_HIDE_PLAYER_NAMES: self._anonymize_hide_player_names,
            statics.KEY_HIDE_PLATFORMS: self._anonymize_hide_platforms,
            statics.KEY_HIDE_QUALITY: self._anonymize_hide_quality,
            statics.KEY_HIDE_BANDWIDTH: self._anonymize_hide_bandwidth,
            statics.KEY_HIDE_TRANSCODING: self._anonymize_hide_transcode_decision,
            statics.KEY_HIDE_PROGRESS: self._anonymize_hide_progress,
            statics.KEY_HIDE_ETA: self._anonymize_hide_eta,
            statics.KEY_USE_FRIENDLY_NAMES: self._use_friendly_names,
            statics.KEY_TIME_MANAGER: self.time_manager,
        }
        return TextManager(rules=rules)


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
    def use_summary_text_message(self) -> bool:
        value = self._connection._get_value(key="PostSummaryMessage", default=True,
                                            env_name_override="TC_DISCORD_POST_SUMMARY_MESSAGE")
        return _extract_bool(value)

    @property
    def channel_name(self) -> str:
        value = self._connection._get_value(key="ChannelName", default="tauticord",
                                            env_name_override="TC_DISCORD_CHANNEL_NAME")
        value = utils.discord_text_channel_name_format(string=value)
        return value

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

        self.tautulli = TautulliConfig(self.config, pull_from_env=self.pull_from_env)
        self.discord = DiscordConfig(self.config, pull_from_env=self.pull_from_env)
        self.extras = ExtrasConfig(self.config, pull_from_env=self.pull_from_env)
        self.performance = {
            statics.KEY_PERFORMANCE_CATEGORY_NAME: self.tautulli._performance_voice_channel_name,
            statics.KEY_PERFORMANCE_MONITOR_CPU: self.extras._performance_monitor_cpu,
            statics.KEY_PERFORMANCE_MONITOR_MEMORY: self.extras._performance_monitor_memory,
        }

        logging.debug(f"Using configuration:\n{self.log()}")

    def __repr__(self) -> str:
        raw_yaml_data = self.config.dump()
        json_data = yaml.load(raw_yaml_data, Loader=yaml.FullLoader)
        return json.dumps(json_data, indent=4)

    @property
    def all(self) -> dict:
        return {
            "Tautulli - Connection - API Key": "Exists" if self.tautulli.api_key else "Not Set",
            "Tautulli - Connection - URL": self.tautulli.url,
            "Tautulli - Connection - Use Self-Signed Cert": self.tautulli.disable_ssl_verification,
            "Tautulli - Customization - Refresh Interval": self.tautulli.refresh_interval,
            "Tautulli - Customization - Server Name": self.tautulli.server_name,
            "Tautulli - Customization - Terminate Message": self.tautulli.terminate_message,
            "Tautulli - Customization - Time Manager": self.tautulli.time_manager,
            "Tautulli - Customization - Voice Channels - Stats - Voice Channel Category Name": self.tautulli.stats_voice_channel_category_name,
            "Tautulli - Customization - Voice Channels - Stats - Display Stream Count": self.tautulli.display_stream_count,
            "Tautulli - Customization - Voice Channels - Stats - Stream Count Channel ID": self.tautulli.stream_count_channel_id,
            "Tautulli - Customization - Voice Channels - Stats - Display Transcode Count": self.tautulli.display_transcode_count,
            "Tautulli - Customization - Voice Channels - Stats - Transcode Count Channel ID": self.tautulli.transcode_count_channel_id,
            "Tautulli - Customization - Voice Channels - Stats - Display Bandwidth": self.tautulli.display_bandwidth,
            "Tautulli - Customization - Voice Channels - Stats - Bandwidth Channel ID": self.tautulli.bandwidth_channel_id,
            "Tautulli - Customization - Voice Channels - Stats - Display Local Bandwidth": self.tautulli.display_local_bandwidth,
            "Tautulli - Customization - Voice Channels - Stats - Local Bandwidth Channel ID": self.tautulli.local_bandwidth_channel_id,
            "Tautulli - Customization - Voice Channels - Stats - Display Remote Bandwidth": self.tautulli.display_remote_bandwidth,
            "Tautulli - Customization - Voice Channels - Stats - Remote Bandwidth Channel ID": self.tautulli.remote_bandwidth_channel_id,
            "Tautulli - Customization - Voice Channels - Stats - Display Plex Status": self.tautulli.display_plex_status,
            "Tautulli - Customization - Voice Channels - Stats - Plex Status Channel ID": self.tautulli.plex_status_channel_id,
            "Tautulli - Customization - Voice Channels - Libraries - Voice Channel Category Name": self.tautulli.libraries_voice_channel_category_name,
            "Tautulli - Customization - Voice Channels - Libraries - Display Library Stats": self.tautulli.display_library_stats,
            "Tautulli - Customization - Voice Channels - Libraries - Library Refresh Interval": self.tautulli.library_refresh_interval,
            "Tautulli - Customization - Voice Channels - Libraries - Library Names": self.tautulli.library_names,
            "Tautulli - Customization - Voice Channels - Libraries - Use Emojis With Library Names": self.tautulli.use_emojis_with_library_names,
            "Tautulli - Customization - Voice Channels - Libraries - Show TV Series Count": self.tautulli.show_tv_series_count,
            "Tautulli - Customization - Voice Channels - Libraries - Show TV Episode Count": self.tautulli.show_tv_episode_count,
            "Tautulli - Customization - Voice Channels - Libraries - Show Music Artist Count": self.tautulli.show_music_artist_count,
            "Tautulli - Customization - Voice Channels - Libraries - Show Music Track Count": self.tautulli.show_music_track_count,
            "Tautulli - Customization - Anonymize - Hide Usernames": self.tautulli._anonymize_hide_usernames,
            "Tautulli - Customization - Anonymize - Hide Platforms": self.tautulli._anonymize_hide_platforms,
            "Tautulli - Customization - Anonymize - Hide Player Names": self.tautulli._anonymize_hide_player_names,
            "Tautulli - Customization - Anonymize - Hide Quality": self.tautulli._anonymize_hide_quality,
            "Tautulli - Customization - Anonymize - Hide Bandwidth": self.tautulli._anonymize_hide_bandwidth,
            "Tautulli - Customization - Anonymize - Hide Transcode Decision": self.tautulli._anonymize_hide_transcode_decision,
            "Tautulli - Customization - Anonymize - Hide Progress": self.tautulli._anonymize_hide_progress,
            "Tautulli - Customization - Anonymize - Hide ETA": self.tautulli._anonymize_hide_eta,
            "Tautulli - Customization - Use Friendly Names": self.tautulli._use_friendly_names,
            "Tautulli - Customization - Thousands Separator": self.tautulli.thousands_separator,
            "Tautulli - Customization - Voice Channels - Performance - Voice Channel Category Name": self.tautulli._performance_voice_channel_name,
            "Discord - Connection - Bot Token": "Exists" if self.discord.bot_token else "Not Set",
            "Discord - Connection - Server ID": self.discord.server_id,
            "Discord - Connection - Admin IDs": self.discord.admin_ids,
            "Discord - Connection - Use Summary Text Message": self.discord.use_summary_text_message,
            "Discord - Connection - Summary Text Channel Name": self.discord.channel_name,
            "Discord - Customization - Has Nitro": self.discord.has_discord_nitro,
            "Extras - Allow Analytics": self.extras.allow_analytics,
            "Extras - Performance - Monitor CPU Performance": self.extras._performance_monitor_cpu,
            "Extras - Performance - Monitor Memory Performance": self.extras._performance_monitor_memory,
        }

    def log(self) -> str:
        return "\n".join([f"{key}: {value}" for key, value in self.all.items()])
