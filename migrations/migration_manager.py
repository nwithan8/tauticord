import os

import modules.logs as logging

from migrations.m001_env_var_to_config_yaml import Migration as Migration001
from migrations.m002_old_config_to_new_config import Migration as Migration002
from migrations.m003_add_recently_added_webhook import Migration as Migration003
from migrations.m004_split_text_channel_names import Migration as Migration004
from migrations.m005_add_seasons_stats  import Migration as Migration005

# NOTE:
# MigrationManager assumes you are using the default tauticord.yaml config file name.
# Does not support custom config file names.


class MigrationManager:
    def __init__(self, migration_data_directory: str, config_directory: str, logs_directory: str):
        self.migration_data_directory = migration_data_directory
        self.config_directory = config_directory
        self.logs_directory = logs_directory

        # Verify directories exist
        os.makedirs(self.migration_data_directory, exist_ok=True)
        os.makedirs(self.config_directory, exist_ok=True)
        os.makedirs(self.logs_directory, exist_ok=True)

        self.migrations = [
            # Copy environment variables to a YAML file (not config.yaml to avoid schema issues)
            Migration001(number="001",
                         migration_data_directory=self.migration_data_directory,
                         config_folder=self.config_directory,
                         logs_folder=self.logs_directory),
            # Convert old config.yaml (or migration file above) to new config.yaml schema
            Migration002(number="002",
                         migration_data_directory=self.migration_data_directory,
                         config_folder=self.config_directory,
                         logs_folder=self.logs_directory),
            # Add "Recently Added" webhook support
            Migration003(number="003",
                         migration_data_directory=self.migration_data_directory,
                         config_folder=self.config_directory,
                         logs_folder=self.logs_directory),
            # Split text channels into two separate channels: one for public announcements and one for private/public monitoring logs
            Migration004(number="004",
                          migration_data_directory=self.migration_data_directory,
                          config_folder=self.config_directory,
                          logs_folder=self.logs_directory),
            # Add "Seasons" stats support
            Migration005(number="005",
                         migration_data_directory=self.migration_data_directory,
                         config_folder=self.config_directory,
                         logs_folder=self.logs_directory),
        ]

    def run_migrations(self) -> bool:
        for migration in self.migrations:
            try:
                if not migration.pre_forward_check():
                    logging.info(f"Migration {migration.number} skipped")
                    continue

                migration.forward()

                if not migration.post_forward_check():
                    logging.error(f"Migration {migration.number} failed")
                    return False  # Exit early, prevent further migrations

                migration.mark_done()
            except Exception as e:
                logging.error(f"Migration {migration.number} failed: {e}")
                return False  # Exit early, prevent further migrations

        return True
