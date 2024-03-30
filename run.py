# Copyright 2023, Nathan Harris.
# All rights reserved.
# Tauticord is released as-is under the "GNU General Public License".
# Please see the LICENSE file that should have been included as part of this package.
import argparse
import os

import modules.discord.discord_connector as discord
import modules.logs as logging
import modules.tautulli.tautulli_connector as tautulli
from consts import (
    GOOGLE_ANALYTICS_ID,
    APP_NAME,
    DEFAULT_CONFIG_PATH,
    DEFAULT_LOG_DIR,
    CONSOLE_LOG_LEVEL,
    FILE_LOG_LEVEL,
)
from migrations.migration_manager import MigrationManager
from modules import versioning
from modules.analytics import GoogleAnalytics
from modules.errors import determine_exit_code
from modules.settings.config_parser import Config
from modules.statics import (
    splash_logo,
    MONITORED_DISK_SPACE_FOLDER,
    KEY_RUN_ARGS_CONFIG_PATH, KEY_RUN_ARGS_LOG_PATH, KEY_RUN_ARGS_MONITOR_PATH,
)

# Parse arguments
parser = argparse.ArgumentParser(description="Tauticord - Discord bot for Tautulli")

"""
Bot will use config, in order:
1. Explicit config file path provided as CLI argument, if included, or
2. Default config file path, if exists, or
3. Environmental variables
"""
parser.add_argument("-c", "--config", help="Path to config file", default=DEFAULT_CONFIG_PATH)
parser.add_argument("-l", "--log", help="Log file directory", default=DEFAULT_LOG_DIR)
parser.add_argument("-u", "--usage", help="Path to directory to monitor for disk usage",
                    default=MONITORED_DISK_SPACE_FOLDER)

args = parser.parse_args()

# Set up logging
logging.init(app_name=APP_NAME, console_log_level=CONSOLE_LOG_LEVEL, log_to_file=True, log_file_dir=args.log,
             file_log_level=FILE_LOG_LEVEL)

# Run migrations
config_directory = os.path.dirname(args.config)
if config_directory == "":
    config_directory = "./"
migration_manager = MigrationManager(
    migration_data_directory=os.path.join(config_directory, "migration_data"),
    config_directory=config_directory,
    logs_directory=args.log)
if not migration_manager.run_migrations():
    logging.fatal("Migrations failed. Exiting...")
    exit(201)

# Set up configuration
kwargs = {
    KEY_RUN_ARGS_MONITOR_PATH: args.usage,
    KEY_RUN_ARGS_CONFIG_PATH: config_directory,
    KEY_RUN_ARGS_LOG_PATH: args.log,
}
config = Config(config_path=f"{args.config}", **kwargs)

# Set up analytics
analytics = GoogleAnalytics(analytics_id=GOOGLE_ANALYTICS_ID,
                            anonymous_ip=True,
                            do_not_track=not config.extras.allow_analytics)


def start():
    logging.info(splash_logo())
    logging.info("Starting Tauticord...")

    # noinspection PyBroadException
    try:
        logging.info("Setting up Tautulli connector")
        tautulli_connector = tautulli.TautulliConnector(
            tautulli_settings=config.tautulli,
            display_settings=config.display,
            stats_settings=config.stats,
            analytics=analytics,
        )

        logging.info("Setting up Discord connector")
        discord_connector = discord.DiscordConnector(
            tautulli_connector=tautulli_connector,
            discord_settings=config.discord,
            tautulli_settings=config.tautulli,
            display_settings=config.display,
            stats_settings=config.stats,
            run_args_settings=config.run_args,
            analytics=analytics,
            version_checker=versioning.VersionChecker(enable=config.extras.update_reminders),
        )

        discord_connector.connect()
    except Exception as e:
        logging.fatal(f"Fatal error occurred. Shutting down: {e}")
        exit_code = determine_exit_code(exception=e)
        logging.fatal(f"Exiting with code {exit_code}")
        exit(exit_code)  # Exit the script if an error bubbles up (like an internet connection error)


if __name__ == '__main__':
    start()
