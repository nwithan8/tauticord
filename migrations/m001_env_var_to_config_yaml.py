import os

import yaml

import legacy.config_parser_v1 as config_parser
from migrations.base import BaseMigration
from migrations.migration_names import MIGRATION_001_CONFIG_FILE, V2_CONFIG_FILE
from legacy.utils import decode_combined_tautulli_libraries


def json_to_yaml(json_data) -> str:
    return yaml.dump(json_data)


class ConfigWriter:
    def __init__(self, config_file_path: str):
        self._config = {}
        self._config_file_path = config_file_path

    def read(self, key_path: list[str]):
        current = self._config
        for key in key_path:
            if key not in current:
                return None
            current = current[key]
        return current

    def add(self, key_path: list[str], value):
        current = self._config
        for key in key_path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[key_path[-1]] = value

    def save(self):
        yaml_data = json_to_yaml(self._config)
        with open(self._config_file_path, 'w') as f:
            f.write(yaml_data)

    @property
    def tautulli_connection_api_key(self) -> str:
        return self.read(key_path=["Tautulli", "Connection", "APIKey"])

    @tautulli_connection_api_key.setter
    def tautulli_connection_api_key(self, value: str):
        self.add(key_path=["Tautulli", "Connection", "APIKey"], value=value)

    @property
    def tautulli_connection_url(self) -> str:
        return self.read(key_path=["Tautulli", "Connection", "URL"])

    @tautulli_connection_url.setter
    def tautulli_connection_url(self, value: str):
        self.add(key_path=["Tautulli", "Connection", "URL"], value=value)

    @property
    def tautulli_connection_use_self_signed_cert(self) -> bool:
        return self.read(key_path=["Tautulli", "Connection", "UseSelfSignedCert"])

    @tautulli_connection_use_self_signed_cert.setter
    def tautulli_connection_use_self_signed_cert(self, value: bool):
        self.add(key_path=["Tautulli", "Connection", "UseSelfSignedCert"], value=value)

    @property
    def tautulli_customization_server_name(self) -> str:
        return self.read(key_path=["Tautulli", "Customization", "ServerName"])

    @tautulli_customization_server_name.setter
    def tautulli_customization_server_name(self, value: str):
        self.add(key_path=["Tautulli", "Customization", "ServerName"], value=value)

    @property
    def tautulli_customization_terminate_message(self) -> str:
        return self.read(key_path=["Tautulli", "Customization", "TerminateMessage"])

    @tautulli_customization_terminate_message.setter
    def tautulli_customization_terminate_message(self, value: str):
        self.add(key_path=["Tautulli", "Customization", "TerminateMessage"], value=value)

    @property
    def tautulli_customization_refresh_seconds(self) -> int:
        return self.read(key_path=["Tautulli", "Customization", "RefreshSeconds"])

    @tautulli_customization_refresh_seconds.setter
    def tautulli_customization_refresh_seconds(self, value: int):
        self.add(key_path=["Tautulli", "Customization", "RefreshSeconds"], value=value)

    @property
    def tautulli_customization_plex_pass(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "PlexPass"])

    @tautulli_customization_plex_pass.setter
    def tautulli_customization_plex_pass(self, value):
        self.add(key_path=["Tautulli", "Customization", "PlexPass"], value=value)

    @property
    def tautulli_customization_server_time_zone(self) -> str:
        return self.read(key_path=["Tautulli", "Customization", "ServerTimeZone"])

    @tautulli_customization_server_time_zone.setter
    def tautulli_customization_server_time_zone(self, value: str):
        self.add(key_path=["Tautulli", "Customization", "ServerTimeZone"], value=value)

    @property
    def tautulli_customization_use_24_hour_time(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "Use24HourTime"])

    @tautulli_customization_use_24_hour_time.setter
    def tautulli_customization_use_24_hour_time(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "Use24HourTime"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_category_name(self) -> str:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "CategoryName"])

    @tautulli_customization_voice_channels_stats_category_name.setter
    def tautulli_customization_voice_channels_stats_category_name(self, value: str):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "CategoryName"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_stream_count(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "StreamCount"])

    @tautulli_customization_voice_channels_stats_stream_count.setter
    def tautulli_customization_voice_channels_stats_stream_count(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "StreamCount"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_stream_count_channel_id(self) -> int:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "StreamCountChannelID"])

    @tautulli_customization_voice_channels_stats_stream_count_channel_id.setter
    def tautulli_customization_voice_channels_stats_stream_count_channel_id(self, value: int):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "StreamCountChannelID"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_transcode_count(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "TranscodeCount"])

    @tautulli_customization_voice_channels_stats_transcode_count.setter
    def tautulli_customization_voice_channels_stats_transcode_count(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "TranscodeCount"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_transcode_count_channel_id(self) -> int:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "TranscodeCountChannelID"])

    @tautulli_customization_voice_channels_stats_transcode_count_channel_id.setter
    def tautulli_customization_voice_channels_stats_transcode_count_channel_id(self, value: int):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "TranscodeCountChannelID"],
                 value=value)

    @property
    def tautulli_customization_voice_channels_stats_bandwidth(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "Bandwidth"])

    @tautulli_customization_voice_channels_stats_bandwidth.setter
    def tautulli_customization_voice_channels_stats_bandwidth(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "Bandwidth"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_bandwidth_channel_id(self) -> int:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "BandwidthChannelID"])

    @tautulli_customization_voice_channels_stats_bandwidth_channel_id.setter
    def tautulli_customization_voice_channels_stats_bandwidth_channel_id(self, value: int):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "BandwidthChannelID"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_local_bandwidth(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "LocalBandwidth"])

    @tautulli_customization_voice_channels_stats_local_bandwidth.setter
    def tautulli_customization_voice_channels_stats_local_bandwidth(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "LocalBandwidth"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_local_bandwidth_channel_id(self) -> int:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "LocalBandwidthChannelID"])

    @tautulli_customization_voice_channels_stats_local_bandwidth_channel_id.setter
    def tautulli_customization_voice_channels_stats_local_bandwidth_channel_id(self, value: int):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "LocalBandwidthChannelID"],
                 value=value)

    @property
    def tautulli_customization_voice_channels_stats_remote_bandwidth(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "RemoteBandwidth"])

    @tautulli_customization_voice_channels_stats_remote_bandwidth.setter
    def tautulli_customization_voice_channels_stats_remote_bandwidth(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "RemoteBandwidth"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_remote_bandwidth_channel_id(self) -> int:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "RemoteBandwidthChannelID"])

    @tautulli_customization_voice_channels_stats_remote_bandwidth_channel_id.setter
    def tautulli_customization_voice_channels_stats_remote_bandwidth_channel_id(self, value: int):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "RemoteBandwidthChannelID"],
                 value=value)

    @property
    def tautulli_customization_voice_channels_stats_plex_status(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "PlexStatus"])

    @tautulli_customization_voice_channels_stats_plex_status.setter
    def tautulli_customization_voice_channels_stats_plex_status(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "PlexStatus"], value=value)

    @property
    def tautulli_customization_voice_channels_stats_plex_status_channel_id(self) -> int:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "PlexStatusChannelID"])

    @tautulli_customization_voice_channels_stats_plex_status_channel_id.setter
    def tautulli_customization_voice_channels_stats_plex_status_channel_id(self, value: int):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Stats", "PlexStatusChannelID"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_category_name(self) -> str:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "CategoryName"])

    @tautulli_customization_voice_channels_libraries_category_name.setter
    def tautulli_customization_voice_channels_libraries_category_name(self, value: str):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "CategoryName"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_enable(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "Enable"])

    @tautulli_customization_voice_channels_libraries_enable.setter
    def tautulli_customization_voice_channels_libraries_enable(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "Enable"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_library_refresh_seconds(self) -> int:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "LibraryRefreshSeconds"])

    @tautulli_customization_voice_channels_libraries_library_refresh_seconds.setter
    def tautulli_customization_voice_channels_libraries_library_refresh_seconds(self, value: int):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "LibraryRefreshSeconds"],
                 value=value)

    @property
    def tautulli_customization_voice_channels_libraries_library_names(self) -> list[str]:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "LibraryNames"])

    @tautulli_customization_voice_channels_libraries_library_names.setter
    def tautulli_customization_voice_channels_libraries_library_names(self, value: list[str]):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "LibraryNames"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_combined_libraries(self) -> dict[str, list[str]]:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "CombinedLibraries"])

    @tautulli_customization_voice_channels_libraries_combined_libraries.setter
    def tautulli_customization_voice_channels_libraries_combined_libraries(self, value: dict[str, list[str]]):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "CombinedLibraries"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_use_emojis(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "UseEmojis"])

    @tautulli_customization_voice_channels_libraries_use_emojis.setter
    def tautulli_customization_voice_channels_libraries_use_emojis(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "UseEmojis"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_tv_series_count(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "TVSeriesCount"])

    @tautulli_customization_voice_channels_libraries_tv_series_count.setter
    def tautulli_customization_voice_channels_libraries_tv_series_count(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "TVSeriesCount"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_tv_episodes_count(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "TVEpisodeCount"])

    @tautulli_customization_voice_channels_libraries_tv_episodes_count.setter
    def tautulli_customization_voice_channels_libraries_tv_episodes_count(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "TVEpisodeCount"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_music_artist_count(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "MusicArtistCount"])

    @tautulli_customization_voice_channels_libraries_music_artist_count.setter
    def tautulli_customization_voice_channels_libraries_music_artist_count(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "MusicArtistCount"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_music_album_count(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "MusicAlbumCount"])

    @tautulli_customization_voice_channels_libraries_music_album_count.setter
    def tautulli_customization_voice_channels_libraries_music_album_count(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "MusicAlbumCount"], value=value)

    @property
    def tautulli_customization_voice_channels_libraries_music_track_count(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "MusicTrackCount"])

    @tautulli_customization_voice_channels_libraries_music_track_count.setter
    def tautulli_customization_voice_channels_libraries_music_track_count(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Libraries", "MusicTrackCount"], value=value)

    @property
    def tautulli_customization_voice_channels_performance_category_name(self) -> str:
        return self.read(key_path=["Tautulli", "Customization", "VoiceChannels", "Performance", "CategoryName"])

    @tautulli_customization_voice_channels_performance_category_name.setter
    def tautulli_customization_voice_channels_performance_category_name(self, value: str):
        self.add(key_path=["Tautulli", "Customization", "VoiceChannels", "Performance", "CategoryName"], value=value)

    @property
    def tautulli_customization_anonymize_hide_usernames(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "Anonymize", "HideUsernames"])

    @tautulli_customization_anonymize_hide_usernames.setter
    def tautulli_customization_anonymize_hide_usernames(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "Anonymize", "HideUsernames"], value=value)

    @property
    def tautulli_customization_anonymize_hide_player_names(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "Anonymize", "HidePlayerNames"])

    @tautulli_customization_anonymize_hide_player_names.setter
    def tautulli_customization_anonymize_hide_player_names(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "Anonymize", "HidePlayerNames"], value=value)

    @property
    def tautulli_customization_anonymize_hide_platforms(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "Anonymize", "HidePlatforms"])

    @tautulli_customization_anonymize_hide_platforms.setter
    def tautulli_customization_anonymize_hide_platforms(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "Anonymize", "HidePlatforms"], value=value)

    @property
    def tautulli_customization_anonymize_hide_quality(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "Anonymize", "HideQuality"])

    @tautulli_customization_anonymize_hide_quality.setter
    def tautulli_customization_anonymize_hide_quality(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "Anonymize", "HideQuality"], value=value)

    @property
    def tautulli_customization_anonymize_hide_bandwidth(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "Anonymize", "HideBandwidth"])

    @tautulli_customization_anonymize_hide_bandwidth.setter
    def tautulli_customization_anonymize_hide_bandwidth(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "Anonymize", "HideBandwidth"], value=value)

    @property
    def tautulli_customization_anonymize_hide_transcode(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "Anonymize", "HideTranscode"])

    @tautulli_customization_anonymize_hide_transcode.setter
    def tautulli_customization_anonymize_hide_transcode(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "Anonymize", "HideTranscode"], value=value)

    @property
    def tautulli_customization_anonymize_hide_progress(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "Anonymize", "HideProgress"])

    @tautulli_customization_anonymize_hide_progress.setter
    def tautulli_customization_anonymize_hide_progress(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "Anonymize", "HideProgress"], value=value)

    @property
    def tautulli_customization_anonymize_hide_eta(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "Anonymize", "HideETA"])

    @tautulli_customization_anonymize_hide_eta.setter
    def tautulli_customization_anonymize_hide_eta(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "Anonymize", "HideETA"], value=value)

    @property
    def tautulli_customization_use_friendly_names(self) -> bool:
        return self.read(key_path=["Tautulli", "Customization", "UseFriendlyNames"])

    @tautulli_customization_use_friendly_names.setter
    def tautulli_customization_use_friendly_names(self, value: bool):
        self.add(key_path=["Tautulli", "Customization", "UseFriendlyNames"], value=value)

    @property
    def tautulli_customization_thousands_separator(self) -> str:
        return self.read(key_path=["Tautulli", "Customization", "ThousandsSeparator"])

    @tautulli_customization_thousands_separator.setter
    def tautulli_customization_thousands_separator(self, value: str):
        self.add(key_path=["Tautulli", "Customization", "ThousandsSeparator"], value=value)

    @property
    def discord_connection_bot_token(self) -> str:
        return self.read(key_path=["Discord", "Connection", "BotToken"])

    @discord_connection_bot_token.setter
    def discord_connection_bot_token(self, value: str):
        self.add(key_path=["Discord", "Connection", "BotToken"], value=value)

    @property
    def discord_connection_server_id(self) -> int:
        return self.read(key_path=["Discord", "Connection", "ServerID"])

    @discord_connection_server_id.setter
    def discord_connection_server_id(self, value: int):
        self.add(key_path=["Discord", "Connection", "ServerID"], value=value)

    @property
    def discord_connection_admin_ids(self) -> list[int]:
        return self.read(key_path=["Discord", "Connection", "AdminIDs"])

    @discord_connection_admin_ids.setter
    def discord_connection_admin_ids(self, value: list[int]):
        self.add(key_path=["Discord", "Connection", "AdminIDs"], value=value)

    @property
    def discord_connection_post_summary_message(self) -> bool:
        return self.read(key_path=["Discord", "Connection", "PostSummaryMessage"])

    @discord_connection_post_summary_message.setter
    def discord_connection_post_summary_message(self, value: bool):
        self.add(key_path=["Discord", "Connection", "PostSummaryMessage"], value=value)

    @property
    def discord_connection_channel_name(self) -> str:
        return self.read(key_path=["Discord", "Connection", "ChannelName"])

    @discord_connection_channel_name.setter
    def discord_connection_channel_name(self, value: str):
        self.add(key_path=["Discord", "Connection", "ChannelName"], value=value)

    @property
    def discord_connection_enable_slash_commands(self) -> bool:
        return self.read(key_path=["Discord", "Connection", "EnableSlashCommands"])

    @discord_connection_enable_slash_commands.setter
    def discord_connection_enable_slash_commands(self, value: bool):
        self.add(key_path=["Discord", "Connection", "EnableSlashCommands"], value=value)

    @property
    def discord_customization_nitro(self) -> bool:
        return self.read(key_path=["Discord", "Customization", "Nitro"])

    @discord_customization_nitro.setter
    def discord_customization_nitro(self, value: bool):
        self.add(key_path=["Discord", "Customization", "Nitro"], value=value)

    @property
    def extras_analytics(self) -> bool:
        return self.read(key_path=["Extras", "Analytics"])

    @extras_analytics.setter
    def extras_analytics(self, value: bool):
        self.add(key_path=["Extras", "Analytics"], value=value)

    @property
    def extras_performance_tautulli_user_count(self) -> bool:
        return self.read(key_path=["Extras", "Performance", "TautulliUserCount"])

    @extras_performance_tautulli_user_count.setter
    def extras_performance_tautulli_user_count(self, value: bool):
        self.add(key_path=["Extras", "Performance", "TautulliUserCount"], value=value)

    @property
    def extras_performance_disk_space(self) -> bool:
        return self.read(key_path=["Extras", "Performance", "DiskSpace"])

    @extras_performance_disk_space.setter
    def extras_performance_disk_space(self, value: bool):
        self.add(key_path=["Extras", "Performance", "DiskSpace"], value=value)

    @property
    def extras_performance_cpu(self) -> bool:
        return self.read(key_path=["Extras", "Performance", "CPU"])

    @extras_performance_cpu.setter
    def extras_performance_cpu(self, value: bool):
        self.add(key_path=["Extras", "Performance", "CPU"], value=value)

    @property
    def extras_performance_memory(self) -> bool:
        return self.read(key_path=["Extras", "Performance", "Memory"])

    @extras_performance_memory.setter
    def extras_performance_memory(self, value: bool):
        self.add(key_path=["Extras", "Performance", "Memory"], value=value)


class Migration(BaseMigration):
    def __init__(self, number: str, migration_data_directory: str, config_folder: str, logs_folder: str):
        super().__init__(number=number, migration_data_directory=migration_data_directory)
        self.config_folder = config_folder
        self.logs_folder = logs_folder
        self._new_config_file_path = f"{migration_data_directory}/{MIGRATION_001_CONFIG_FILE}"

    def pre_forward_check(self) -> bool:
        # If the new config file already exists, we don't need to do anything
        if os.path.isfile(f"{self.config_folder}/{V2_CONFIG_FILE}"):
            return False

        return True

    def forward(self):
        self.log(f"Copying environment variables to {self._new_config_file_path}")

        old_config = config_parser.Config(app_name="Migration", config_path="does_not_matter_wont_be_found.yaml",
                                          fallback_to_env=True, **{})

        new_config = ConfigWriter(config_file_path=self._new_config_file_path)
        new_config.tautulli_connection_url = old_config.tautulli.url
        new_config.tautulli_connection_api_key = old_config.tautulli.api_key
        new_config.tautulli_connection_use_self_signed_cert = old_config.tautulli.disable_ssl_verification
        new_config.tautulli_customization_refresh_seconds = old_config.tautulli.refresh_interval
        new_config.tautulli_customization_server_name = old_config.tautulli.server_name
        new_config.tautulli_customization_terminate_message = old_config.tautulli.terminate_message
        new_config.tautulli_customization_server_time_zone = old_config.tautulli._customization._get_value(
            key='ServerTimeZone', default=None, env_name_override="TZ")
        use_24_hour_time = old_config.tautulli._customization._get_value(key='Use24HourTime', default=False,
                                                                         env_name_override="TC_USE_24_HOUR_TIME")
        new_config.tautulli_customization_use_24_hour_time = config_parser._extract_bool(value=use_24_hour_time)
        new_config.tautulli_customization_voice_channels_stats_category_name = old_config.tautulli.stats_voice_channel_category_name
        new_config.tautulli_customization_voice_channels_stats_stream_count = old_config.tautulli.display_stream_count
        new_config.tautulli_customization_voice_channels_stats_stream_count_channel_id = old_config.tautulli.stream_count_channel_id
        new_config.tautulli_customization_voice_channels_stats_transcode_count = old_config.tautulli.display_transcode_count
        new_config.tautulli_customization_voice_channels_stats_transcode_count_channel_id = old_config.tautulli.transcode_count_channel_id
        new_config.tautulli_customization_voice_channels_stats_bandwidth = old_config.tautulli.display_bandwidth
        new_config.tautulli_customization_voice_channels_stats_bandwidth_channel_id = old_config.tautulli.bandwidth_channel_id
        new_config.tautulli_customization_voice_channels_stats_local_bandwidth = old_config.tautulli.display_local_bandwidth
        new_config.tautulli_customization_voice_channels_stats_local_bandwidth_channel_id = old_config.tautulli.local_bandwidth_channel_id
        new_config.tautulli_customization_voice_channels_stats_remote_bandwidth = old_config.tautulli.display_remote_bandwidth
        new_config.tautulli_customization_voice_channels_stats_remote_bandwidth_channel_id = old_config.tautulli.remote_bandwidth_channel_id
        new_config.tautulli_customization_voice_channels_stats_plex_status = old_config.tautulli.display_plex_status
        new_config.tautulli_customization_voice_channels_stats_plex_status_channel_id = old_config.tautulli.plex_status_channel_id
        new_config.tautulli_customization_voice_channels_libraries_enable = old_config.tautulli.display_library_stats
        new_config.tautulli_customization_voice_channels_libraries_library_refresh_seconds = old_config.tautulli.library_refresh_interval
        new_config.tautulli_customization_voice_channels_libraries_category_name = old_config.tautulli.libraries_voice_channel_category_name
        new_config.tautulli_customization_voice_channels_libraries_library_names = old_config.tautulli.library_names
        combined_libraries_decoded = {}
        for encoded in old_config.tautulli.combined_library_names:
            name, libraries = decode_combined_tautulli_libraries(encoded_string=encoded)
            combined_libraries_decoded[name] = libraries
        new_config.tautulli_customization_voice_channels_libraries_combined_libraries = combined_libraries_decoded
        new_config.tautulli_customization_voice_channels_libraries_use_emojis = old_config.tautulli.use_emojis_with_library_names
        new_config.tautulli_customization_voice_channels_libraries_tv_series_count = old_config.tautulli.show_tv_series_count
        new_config.tautulli_customization_voice_channels_libraries_tv_episodes_count = old_config.tautulli.show_tv_episode_count
        new_config.tautulli_customization_voice_channels_libraries_music_artist_count = old_config.tautulli.show_music_artist_count
        new_config.tautulli_customization_voice_channels_libraries_music_album_count = old_config.tautulli.show_music_album_count
        new_config.tautulli_customization_voice_channels_libraries_music_track_count = old_config.tautulli.show_music_track_count
        new_config.tautulli_customization_anonymize_hide_usernames = old_config.tautulli._anonymize_hide_usernames
        new_config.tautulli_customization_anonymize_hide_platforms = old_config.tautulli._anonymize_hide_platforms
        new_config.tautulli_customization_anonymize_hide_player_names = old_config.tautulli._anonymize_hide_player_names
        new_config.tautulli_customization_anonymize_hide_quality = old_config.tautulli._anonymize_hide_quality
        new_config.tautulli_customization_anonymize_hide_bandwidth = old_config.tautulli._anonymize_hide_bandwidth
        new_config.tautulli_customization_anonymize_hide_transcode = old_config.tautulli._anonymize_hide_transcode_decision
        new_config.tautulli_customization_anonymize_hide_progress = old_config.tautulli._anonymize_hide_progress
        new_config.tautulli_customization_anonymize_hide_eta = old_config.tautulli._anonymize_hide_eta
        new_config.tautulli_customization_use_friendly_names = old_config.tautulli._use_friendly_names
        new_config.tautulli_customization_thousands_separator = old_config.tautulli.thousands_separator
        new_config.tautulli_customization_voice_channels_performance_category_name = old_config.tautulli._performance_voice_channel_category_name
        new_config.discord_connection_bot_token = old_config.discord.bot_token
        new_config.discord_connection_server_id = old_config.discord.server_id
        new_config.discord_connection_admin_ids = old_config.discord.admin_ids
        new_config.discord_connection_post_summary_message = old_config.discord.use_summary_text_message
        new_config.discord_connection_channel_name = old_config.discord.channel_name
        new_config.discord_connection_enable_slash_commands = old_config.discord.enable_slash_commands
        new_config.discord_customization_nitro = old_config.discord.has_discord_nitro
        new_config.extras_analytics = old_config.extras.allow_analytics
        new_config.extras_performance_tautulli_user_count = old_config.extras._performance_monitor_tautulli_user_count
        new_config.extras_performance_disk_space = old_config.extras._performance_monitor_disk_space
        new_config.extras_performance_cpu = old_config.extras._performance_monitor_cpu
        new_config.extras_performance_memory = old_config.extras._performance_monitor_memory

        # Write config file to disk
        new_config.save()

    def post_forward_check(self) -> bool:
        # Make sure the new config file was created
        return os.path.exists(self._new_config_file_path)

    def backwards(self):
        self.mark_undone()
