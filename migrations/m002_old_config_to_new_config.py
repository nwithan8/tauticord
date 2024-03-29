import os
import shutil

import yaml

import legacy.config_parser_v1 as config_parser
from migrations.base import BaseMigration
from migrations.migration_names import CONFIG_FILE, MIGRATION_001_CONFIG_FILE, MIGRATION_002_CONFIG_FILE
from modules.utils import decode_combined_tautulli_libraries


def json_to_yaml(json_data) -> str:
    return yaml.dump(json_data)


def value_exists(value):
    return value is not None and value != ""


def path_exists_in_yaml(yaml_data, path: list[str]) -> bool:
    current = yaml_data
    for key in path:
        if key not in current:
            return False
        current = current[key]
    return True


class ConfigWriter:
    def __init__(self, config_file_path: str):
        self._config = {}
        self._config_file_path = config_file_path

    def add(self, value, key_path: list[str]):
        current = self._config
        for key in key_path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[key_path[-1]] = value

    def migrate_value(self, value, to_path: list[str]):
        if value is None:
            return
        self.add(value=value, key_path=to_path)

    def build_voice_channel_config(self, parent_path: list[str], channel_name: str, enabled: bool, use_emojis: bool,
                                   custom_emoji: str = "", voice_channel_id: int = 0, additional_pairs: dict = None):
        self.migrate_value(value=enabled, to_path=parent_path + [channel_name, "Enable"])
        self.migrate_value(value=use_emojis, to_path=parent_path + [channel_name, "UseEmojis"])
        self.migrate_value(value=custom_emoji, to_path=parent_path + [channel_name, "CustomEmoji"])
        self.migrate_value(value=voice_channel_id, to_path=parent_path + [channel_name, "VoiceChannelID"])
        additional_pairs = additional_pairs or {}
        for key, value in additional_pairs.items():
            self.migrate_value(value=value, to_path=parent_path + [channel_name, key])

    def save(self):
        yaml_data = json_to_yaml(self._config)
        with open(self._config_file_path, 'w') as f:
            f.write(yaml_data)


class Migration(BaseMigration):
    def __init__(self, number: str, migration_tracker_folder: str, config_folder: str, logs_folder: str):
        super().__init__(number=number, migration_tracker_folder=migration_tracker_folder)
        self.config_folder = config_folder
        self.logs_folder = logs_folder
        self.old_config_file = f"{self.config_folder}/{CONFIG_FILE}"
        self.new_config_file = f"{self.config_folder}/{MIGRATION_002_CONFIG_FILE}"

    def pre_forward_check(self) -> bool:
        # Make sure we have the old config file and it's still the old schema
        if os.path.isfile(self.old_config_file):
            with open(self.old_config_file, 'r') as f:
                data = yaml.safe_load(f)
                # This path is only in the new schema. If it exists, it's the new schema
                if path_exists_in_yaml(yaml_data=data, path=["Stats", "Activity", "Enable"]):
                    self.log(f"Config file at {self.old_config_file} is already in the new schema")
                    return False
            return True

        self.log(f"Could not find old config file at {self.old_config_file}, trying {MIGRATION_001_CONFIG_FILE}")

        # Check if we have the migration 001 config file
        if os.path.isfile(f"{self.config_folder}/{MIGRATION_001_CONFIG_FILE}"):
            self.old_config_file = f"{self.config_folder}/{MIGRATION_001_CONFIG_FILE}"
            return True

        self.error(f"Could not find old config file to migrate")
        return False

    def forward(self):
        self.log("Migrating old config to new config schema")

        old_config = config_parser.Config(app_name="Migration", config_path=self.old_config_file,
                                          fallback_to_env=False, **{})
        new_config = ConfigWriter(config_file_path=self.new_config_file)

        # Tautulli
        new_config.migrate_value(value=old_config.tautulli.url, to_path=["Tautulli", "URL"])
        new_config.migrate_value(value=old_config.tautulli.api_key, to_path=["Tautulli", "APIKey"])
        new_config.migrate_value(value=old_config.tautulli.disable_ssl_verification,
                                 to_path=["Tautulli", "UseSelfSignedCert"])
        new_config.migrate_value(value=old_config.tautulli.refresh_interval, to_path=["Tautulli", "RefreshSeconds"])
        new_config.migrate_value(value=old_config.tautulli.terminate_message, to_path=["Tautulli", "TerminateMessage"])
        # Plex Pass setting no longer used

        # Discord
        new_config.migrate_value(value=old_config.discord.bot_token, to_path=["Discord", "BotToken"])
        new_config.migrate_value(value=old_config.discord.server_id, to_path=["Discord", "ServerID"])
        new_config.migrate_value(value=old_config.discord.admin_ids, to_path=["Discord", "AdminIDs"])
        new_config.migrate_value(value=old_config.discord.use_summary_text_message,
                                 to_path=["Discord", "PostSummaryMessage"])
        new_config.migrate_value(value=old_config.discord.channel_name, to_path=["Discord", "ChannelName"])
        new_config.migrate_value(value=old_config.discord.enable_slash_commands,
                                 to_path=["Discord", "EnableSlashCommands"])
        new_config.migrate_value(value=old_config.discord.has_discord_nitro, to_path=["Discord", "Nitro"])

        # Display
        new_config.migrate_value(value=old_config.tautulli.server_name, to_path=["Display", "ServerName"])
        new_config.migrate_value(value=old_config.tautulli._use_friendly_names, to_path=["Display", "UseFriendlyNames"])
        new_config.migrate_value(value=old_config.tautulli.thousands_separator,
                                 to_path=["Display", "ThousandsSeparator"])
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_usernames,
                                 to_path=["Display", "Anonymize", "HideUsernames"])
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_platforms,
                                 to_path=["Display", "Anonymize", "HidePlatforms"])
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_player_names,
                                 to_path=["Display", "Anonymize", "HidePlayerNames"])
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_quality,
                                 to_path=["Display", "Anonymize", "HideQuality"])
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_bandwidth,
                                 to_path=["Display", "Anonymize", "HideBandwidth"])
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_transcode_decision,
                                 to_path=["Display", "Anonymize", "HideTranscode"])
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_progress,
                                 to_path=["Display", "Anonymize", "HideProgress"])
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_eta,
                                 to_path=["Display", "Anonymize", "HideETA"])
        new_config.migrate_value(
            value=old_config.tautulli._customization._get_value(key='Use24HourTime', default=False),
            to_path=["Display", "Time", "Use24HourTime"])
        new_config.migrate_value(
            value=old_config.tautulli._customization._get_value(key='ServerTimeZone', default=None),
            to_path=["Display", "Time", "ServerTimeZone"])

        # Stats
        new_config.add(value=any([
            old_config.tautulli.display_stream_count,
            old_config.tautulli.display_transcode_count,
            old_config.tautulli.display_bandwidth,
            old_config.tautulli.display_local_bandwidth,
            old_config.tautulli.display_remote_bandwidth,
            old_config.tautulli.display_plex_status
        ]), key_path=["Stats", "Activity", "Enable"])
        new_config.migrate_value(value=old_config.tautulli.stats_voice_channel_category_name,
                                 to_path=["Stats", "Activity", "CategoryName"])
        channels = {
            'StreamCount': old_config.tautulli.display_stream_count,
            'TranscodeCount': old_config.tautulli.display_transcode_count,
            'Bandwidth': old_config.tautulli.display_bandwidth,
            'LocalBandwidth': old_config.tautulli.display_local_bandwidth,
            'RemoteBandwidth': old_config.tautulli.display_remote_bandwidth,
            'PlexServerAvailability': old_config.tautulli.display_plex_status
        }
        for channel_type, enabled in channels.items():
            new_config.build_voice_channel_config(parent_path=["Stats", "Activity", "StatTypes"],
                                                  channel_name=channel_type, enabled=enabled,
                                                  use_emojis=old_config.tautulli.use_emojis_with_library_names,
                                                  voice_channel_id=0)
        new_config.migrate_value(value=old_config.tautulli.display_library_stats,
                                 to_path=["Stats", "Libraries", "Enable"])
        new_config.migrate_value(value=old_config.tautulli.libraries_voice_channel_category_name,
                                 to_path=["Stats", "Libraries", "CategoryName"])
        new_config.migrate_value(value=old_config.tautulli.library_refresh_interval,
                                 to_path=["Stats", "Libraries", "RefreshSeconds"])
        new_config.add(value={}, key_path=["Stats", "Libraries", "Libraries"])
        for library in old_config.tautulli.library_names:
            new_config.add(value=library, key_path=["Stats", "Libraries", "Libraries", library, "AlternateName"])
            channels = {
                'Series': old_config.tautulli.show_tv_series_count,
                'Episodes': old_config.tautulli.show_tv_episode_count,
                'Artists': old_config.tautulli.show_music_artist_count,
                'Albums': old_config.tautulli.show_music_album_count,
                'Tracks': old_config.tautulli.show_music_track_count
            }
            for channel_type, enabled in channels.items():
                new_config.build_voice_channel_config(parent_path=["Stats", "Libraries", "Libraries", library],
                                                      channel_name=channel_type, enabled=enabled,
                                                      use_emojis=old_config.tautulli.use_emojis_with_library_names,
                                                      voice_channel_id=0)
        new_config.add(value={}, key_path=["Stats", "Libraries", "CombinedLibraries"])
        for encoded in old_config.tautulli.combined_library_names:
            name, libraries = decode_combined_tautulli_libraries(encoded_string=encoded)
            new_config.add(value=libraries, key_path=["Stats", "Libraries", "CombinedLibraries", name, "Libraries"])
            channels = {
                'Series': old_config.tautulli.show_tv_series_count,
                'Episodes': old_config.tautulli.show_tv_episode_count,
                'Artists': old_config.tautulli.show_music_artist_count,
                'Albums': old_config.tautulli.show_music_album_count,
                'Tracks': old_config.tautulli.show_music_track_count
            }
            for channel_type, enabled in channels.items():
                new_config.build_voice_channel_config(parent_path=["Stats", "Libraries", "CombinedLibraries", name],
                                                      channel_name=channel_type, enabled=enabled,
                                                      use_emojis=old_config.tautulli.use_emojis_with_library_names,
                                                      voice_channel_id=0)
        new_config.add(value=any([
            old_config.extras._performance_monitor_tautulli_user_count,
            old_config.extras._performance_monitor_disk_space,
            old_config.extras._performance_monitor_cpu,
            old_config.extras._performance_monitor_memory
        ]), key_path=["Stats", "Performance", "Enable"])
        new_config.migrate_value(value=old_config.tautulli._performance_voice_channel_category_name,
                                 to_path=["Stats", "Performance", "CategoryName"])
        channels = {
            'UserCount': old_config.extras._performance_monitor_tautulli_user_count,
            'DiskSpace': old_config.extras._performance_monitor_disk_space,
            'CPU': old_config.extras._performance_monitor_cpu,
            'Memory': old_config.extras._performance_monitor_memory
        }
        for channel_type, enabled in channels.items():
            new_config.build_voice_channel_config(parent_path=["Stats", "Performance", "Metrics"],
                                                  channel_name=channel_type, enabled=enabled,
                                                  use_emojis=old_config.tautulli.use_emojis_with_library_names,
                                                  voice_channel_id=0)

        # Extras
        new_config.migrate_value(value=old_config.extras.allow_analytics, to_path=["Extras", "Analytics"])

        # Write config file to disk
        new_config.save()

        # Copy the file to config.yaml
        shutil.copy(self.new_config_file, f"{self.config_folder}/config.yaml")

    def post_forward_check(self) -> bool:
        # Make sure the new config file was created
        return os.path.isfile(self.new_config_file) and os.path.isfile(f"{self.config_folder}/config.yaml")

    def backwards(self):
        self.mark_undone()
