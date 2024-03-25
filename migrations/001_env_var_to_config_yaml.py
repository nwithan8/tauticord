# Need to import the modules folder
import shutil
import sys
sys.path.append('./')  # Relative to "tauticord" folder when run from "tauticord" folder

import argparse

from base import BaseMigration

import modules.settings.config_parser as config_parser
import modules.settings.config_writer as config_writer
from modules.utils import decode_combined_tautulli_libraries

class Migration(BaseMigration):
    def __init__(self, number: str, migration_tracker: str, config_folder: str, logs_folder: str):
        super().__init__(number=number, migration_file=migration_tracker)
        self.config_folder = config_folder
        self.logs_folder = logs_folder

    def forward(self):
        new_config_file_path = "migrated_config.yaml"
        self.log(f"Copying environment variables to {new_config_file_path}")

        old_config = config_parser.Config(app_name="Migration", config_path="does_not_matter_wont_be_found.yaml",
                                          fallback_to_env=True, **{})

        new_config = config_writer.ConfigWriter(config_file_path=new_config_file_path)
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
        # Move config file to correct location
        shutil.move(src=new_config_file_path, dst=f"{self.config_folder}/{new_config_file_path}")

        self.mark_done()

    def backwards(self):
        self.log("Hello from migration 001")

        self.mark_undone()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Migration 001 - Copy environment variables to config.yaml")
    parser.add_argument("migration_tracker", help="Path to migration tracker file")
    parser.add_argument("config_folder", help="Path to config folder")
    parser.add_argument("logs_folder", help="Path to logs folder")
    args = parser.parse_args()

    Migration(number="001", migration_tracker=args.migration_tracker, config_folder=args.config_folder,
              logs_folder=args.logs_folder).forward()
