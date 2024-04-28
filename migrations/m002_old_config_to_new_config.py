import os
import shutil

import yaml

import legacy.config_parser_v1 as config_parser
from legacy.utils import decode_combined_tautulli_libraries
from migrations.base import BaseMigration
from migrations.migration_names import V1_CONFIG_FILE, V2_CONFIG_FILE, MIGRATION_001_CONFIG_FILE, \
    MIGRATION_002_CONFIG_FILE


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

    def migrate_value(self, value, to_path: list[str], default=None):
        if (value is None or value == "None") and default is not None:
            value = default
        self.add(value=value, key_path=to_path)

    def build_voice_channel_config(self, enabled: bool, custom_name: str = "", custom_emoji: str = "",
                                   voice_channel_id: int = 0, additional_pairs: dict = None) -> dict:
        config = {
            "Enable": enabled,
            "CustomName": custom_name,
            "CustomEmoji": custom_emoji,
            "VoiceChannelID": voice_channel_id
        }
        additional_pairs = additional_pairs or {}
        for key, value in additional_pairs.items():
            config[key] = value

        return config

    def save(self):
        yaml_data = json_to_yaml(self._config)
        with open(self._config_file_path, 'w') as f:
            f.write(yaml_data)


class Migration(BaseMigration):
    def __init__(self, number: str, migration_data_directory: str, config_folder: str, logs_folder: str):
        super().__init__(number=number, migration_data_directory=migration_data_directory)
        self.config_folder = config_folder
        self.logs_folder = logs_folder
        self.old_config_file = f"{self.config_folder}/{V1_CONFIG_FILE}"
        self.new_config_file = f"{migration_data_directory}/{MIGRATION_002_CONFIG_FILE}"

    def is_file_in_new_schema(self, file_path: str) -> bool:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            # This path is only in the new schema. If it exists, it's the new schema
            return path_exists_in_yaml(yaml_data=data, path=["Stats", "Activity", "Enable"])

    def pre_forward_check(self) -> bool:
        # If the new config file already exists, we don't need to do anything
        if os.path.isfile(f"{self.config_folder}/{V2_CONFIG_FILE}"):
            # Delete the old config file
            try:
                os.remove(f"{self.config_folder}/{V1_CONFIG_FILE}")
            except FileNotFoundError:
                pass
            return False

        # Make sure we have the old config file
        if os.path.isfile(self.old_config_file):

            # If the config.yaml file is already in the new schema, we just need to move it
            if self.is_file_in_new_schema(file_path=self.old_config_file):
                self.log(f"Config file at {self.old_config_file} is already in the new schema, moving...")
                shutil.move(self.old_config_file, f"{self.config_folder}/{V2_CONFIG_FILE}")
                return False

            # Otherwise, we need to migrate the old config file
            return True

        # If we don't have the old config file available, try using the migration 001 config file
        self.log(f"Could not find old config file at {self.old_config_file}, trying {MIGRATION_001_CONFIG_FILE}")
        if os.path.isfile(f"{self.migration_data_directory}/{MIGRATION_001_CONFIG_FILE}"):
            self.old_config_file = f"{self.migration_data_directory}/{MIGRATION_001_CONFIG_FILE}"
            return True

        # Otherwise, we can't migrate anything
        self.error(f"Could not find old config file to migrate")
        return False

    def forward(self):
        self.log("Migrating old config to new config schema")

        old_config = config_parser.Config(app_name="Migration", config_path=self.old_config_file,
                                          fallback_to_env=False, **{})
        new_config = ConfigWriter(config_file_path=self.new_config_file)

        # Tautulli
        new_config.migrate_value(value=old_config.tautulli.url, to_path=["Tautulli", "URL"], default="")
        new_config.migrate_value(value=old_config.tautulli.api_key, to_path=["Tautulli", "APIKey"], default="")
        new_config.migrate_value(value=old_config.tautulli.disable_ssl_verification,
                                 to_path=["Tautulli", "UseSelfSignedCert"], default=False)
        new_config.migrate_value(value=old_config.tautulli.refresh_interval, to_path=["Tautulli", "RefreshSeconds"],
                                 default=15)
        new_config.migrate_value(value=old_config.tautulli.terminate_message, to_path=["Tautulli", "TerminateMessage"],
                                 default="")
        # Plex Pass setting no longer used

        # Discord
        new_config.migrate_value(value=old_config.discord.bot_token, to_path=["Discord", "BotToken"], default="")
        new_config.migrate_value(value=old_config.discord.server_id, to_path=["Discord", "ServerID"], default="0")
        new_config.migrate_value(value=old_config.discord.admin_ids, to_path=["Discord", "AdminIDs"], default=[])
        new_config.migrate_value(value=old_config.discord.use_summary_text_message,
                                 to_path=["Discord", "PostSummaryMessage"], default=True)
        new_config.migrate_value(value=old_config.discord.channel_name, to_path=["Discord", "ChannelName"])
        new_config.add(value=True, key_path=["Discord", "EnableTermination"])
        new_config.migrate_value(value=old_config.discord.enable_slash_commands,
                                 to_path=["Discord", "EnableSlashCommands"], default=False)
        status_message_settings = {
            "Enable": True,
            "CustomMessage": "",
            "ShowStreamCount": True,
        }
        new_config.add(value=status_message_settings, key_path=["Discord", "StatusMessage"])

        # Display
        new_config.migrate_value(value=old_config.tautulli.server_name, to_path=["Display", "ServerName"],
                                 default="Plex Server")
        new_config.migrate_value(value=old_config.tautulli._use_friendly_names, to_path=["Display", "UseFriendlyNames"],
                                 default=False)
        new_config.migrate_value(value=old_config.tautulli.thousands_separator,
                                 to_path=["Display", "ThousandsSeparator"], default="")
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_usernames,
                                 to_path=["Display", "Anonymize", "HideUsernames"], default=False)
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_platforms,
                                 to_path=["Display", "Anonymize", "HidePlatforms"], default=False)
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_player_names,
                                 to_path=["Display", "Anonymize", "HidePlayerNames"], default=False)
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_quality,
                                 to_path=["Display", "Anonymize", "HideQuality"], default=False)
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_bandwidth,
                                 to_path=["Display", "Anonymize", "HideBandwidth"], default=False)
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_transcode_decision,
                                 to_path=["Display", "Anonymize", "HideTranscode"], default=False)
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_progress,
                                 to_path=["Display", "Anonymize", "HideProgress"], default=False)
        new_config.migrate_value(value=old_config.tautulli._anonymize_hide_eta,
                                 to_path=["Display", "Anonymize", "HideETA"], default=False)
        new_config.migrate_value(
            value=old_config.tautulli._customization._get_value(key='Use24HourTime', default=False),
            to_path=["Display", "Time", "Use24HourTime"], default=False)
        new_config.migrate_value(
            value=old_config.tautulli._customization._get_value(key='ServerTimeZone', default="UTC"),
            to_path=["Display", "Time", "ServerTimeZone"], default="UTC")

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
                                 to_path=["Stats", "Activity", "CategoryName"], default="Plex Stats")
        channels = {
            'StreamCount': old_config.tautulli.display_stream_count,
            'TranscodeCount': old_config.tautulli.display_transcode_count,
            'Bandwidth': old_config.tautulli.display_bandwidth,
            'LocalBandwidth': old_config.tautulli.display_local_bandwidth,
            'RemoteBandwidth': old_config.tautulli.display_remote_bandwidth,
            'PlexServerAvailability': old_config.tautulli.display_plex_status
        }
        stat_types = {}
        for channel_type, enabled in channels.items():
            channel_config = new_config.build_voice_channel_config(enabled=enabled,
                                                                   voice_channel_id=0)
            stat_types[channel_type] = channel_config

        new_config.add(value=stat_types, key_path=["Stats", "Activity", "StatTypes"])
        new_config.migrate_value(value=old_config.tautulli.display_library_stats,
                                 to_path=["Stats", "Libraries", "Enable"], default=False)
        new_config.migrate_value(value=old_config.tautulli.libraries_voice_channel_category_name,
                                 to_path=["Stats", "Libraries", "CategoryName"], default="Plex Libraries")
        new_config.migrate_value(value=old_config.tautulli.library_refresh_interval,
                                 to_path=["Stats", "Libraries", "RefreshSeconds"], default=3600)

        library_configs = []
        for library in old_config.tautulli.library_names:
            library_config = {
                "Name": library,
                "ID": 0,
                "AlternateName": "",
            }
            channels = {
                'Movies': True,
                'Series': old_config.tautulli.show_tv_series_count,
                'Episodes': old_config.tautulli.show_tv_episode_count,
                'Artists': old_config.tautulli.show_music_artist_count,
                'Albums': old_config.tautulli.show_music_album_count,
                'Tracks': old_config.tautulli.show_music_track_count
            }
            for channel_type, enabled in channels.items():
                channel_config = new_config.build_voice_channel_config(enabled=enabled,
                                                                       voice_channel_id=0)
                library_config[channel_type] = channel_config
            library_configs.append(library_config)
        new_config.add(value=library_configs, key_path=["Stats", "Libraries", "Libraries"])

        combined_library_configs = []
        for encoded in old_config.tautulli.combined_library_names:
            name, libraries = decode_combined_tautulli_libraries(encoded_string=encoded)
            libraries_config = []
            for library in libraries:
                libraries_config.append({
                    "Name": library,
                    "ID": 0
                })
            library_config = {
                "Name": name,
                "Libraries": libraries_config,
            }
            channels = {
                'Movies': True,
                'Series': old_config.tautulli.show_tv_series_count,
                'Episodes': old_config.tautulli.show_tv_episode_count,
                'Artists': old_config.tautulli.show_music_artist_count,
                'Albums': old_config.tautulli.show_music_album_count,
                'Tracks': old_config.tautulli.show_music_track_count
            }
            for channel_type, enabled in channels.items():
                channel_config = new_config.build_voice_channel_config(enabled=enabled,
                                                                       voice_channel_id=0)
                library_config[channel_type] = channel_config
            combined_library_configs.append(library_config)
        new_config.add(value=combined_library_configs, key_path=["Stats", "Libraries", "CombinedLibraries"])

        new_config.add(value=any([
            old_config.extras._performance_monitor_tautulli_user_count,
            old_config.extras._performance_monitor_disk_space,
            old_config.extras._performance_monitor_cpu,
            old_config.extras._performance_monitor_memory
        ]), key_path=["Stats", "Performance", "Enable"])
        new_config.migrate_value(value=old_config.tautulli._performance_voice_channel_category_name,
                                 to_path=["Stats", "Performance", "CategoryName"], default="Performance")
        channels = {
            'UserCount': old_config.extras._performance_monitor_tautulli_user_count,
            'DiskSpace': old_config.extras._performance_monitor_disk_space,
            'CPU': old_config.extras._performance_monitor_cpu,
            'Memory': old_config.extras._performance_monitor_memory
        }
        for channel_type, enabled in channels.items():
            channel_config = new_config.build_voice_channel_config(enabled=enabled,
                                                                   voice_channel_id=0)
            new_config.add(value=channel_config, key_path=["Stats", "Performance", "Metrics", channel_type])

        # Extras
        new_config.migrate_value(value=old_config.extras.allow_analytics, to_path=["Extras", "AllowAnalytics"],
                                 default=True)
        new_config.add(value=True, key_path=["Extras", "EnableUpdateReminders"])

        # Write config file to disk
        new_config.save()

        # Add YAML language server link at the top of the file
        with open(self.new_config_file, 'r') as f:
            data = f.read()
        with open(self.new_config_file, 'w') as f:
            f.write(
                "# yaml-language-server: $schema=https://raw.githubusercontent.com/nwithan8/tauticord/master/.schema/config_v2.schema.json\n\n")
            f.write(data)

        # Copy (not replace) the file to new config file location
        shutil.copy(self.new_config_file, f"{self.config_folder}/{V2_CONFIG_FILE}")
        # Delete the old config file
        try:
            os.remove(f"{self.config_folder}/{V1_CONFIG_FILE}")
        except FileNotFoundError:
            pass

    def post_forward_check(self) -> bool:
        # Make sure the new config file was created
        return os.path.isfile(self.new_config_file) and os.path.isfile(f"{self.config_folder}/{V2_CONFIG_FILE}")

    def backwards(self):
        self.mark_undone()
