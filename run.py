import argparse
import os

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
from modules.discord.bot import Bot
from modules.discord.services.library_stats import LibraryStatsMonitor
from modules.discord.services.live_activity import LiveActivityMonitor
from modules.discord.services.performance_stats import PerformanceStatsMonitor
from modules.discord.services.slash_commands import SlashCommandManager
from modules.discord.services.tagged_message import TaggedMessagesManager
from modules.emojis import EmojiManager
from modules.settings.config_parser import Config
from modules.statics import (
    splash_logo,
    MONITORED_DISK_SPACE_FOLDER,
    KEY_RUN_ARGS_CONFIG_PATH, KEY_RUN_ARGS_LOG_PATH, KEY_RUN_ARGS_MONITOR_PATH,
)

# Parse CLI arguments
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
logging.info(splash_logo())

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

# Set up Tautulli connection
logging.info("Setting up Tautulli connection")
tautulli_connector = tautulli.TautulliConnector(
    tautulli_settings=config.tautulli,
    display_settings=config.display,
    stats_settings=config.stats,
    analytics=analytics,
)

# Set up emoji manager
emoji_manager = EmojiManager()

# Set up Discord bot
services = [
    # Services start in the order they are added
    SlashCommandManager(
        enable_slash_commands=config.discord.enable_slash_commands,
        guild_id=config.discord.server_id,
        tautulli=tautulli_connector,
        emoji_manager=emoji_manager,
        admin_ids=config.discord.admin_ids,
    ),
    TaggedMessagesManager(
        guild_id=config.discord.server_id,
        emoji_manager=emoji_manager,
        admin_ids=config.discord.admin_ids,
    ),
    LiveActivityMonitor(
        tautulli_connector=tautulli_connector,
        discord_settings=config.discord,
        tautulli_settings=config.tautulli,
        stats_settings=config.stats,
        emoji_manager=emoji_manager,
        analytics=analytics,
        version_checker=versioning.VersionChecker(enable=config.extras.update_reminders)
    ),
    LibraryStatsMonitor(
        tautulli_connector=tautulli_connector,
        discord_settings=config.discord,
        stats_settings=config.stats,
        emoji_manager=emoji_manager,
        analytics=analytics,
    ),
    PerformanceStatsMonitor(
        tautulli_connector=tautulli_connector,
        discord_settings=config.discord,
        stats_settings=config.stats,
        run_args_settings=config.run_args,
        emoji_manager=emoji_manager,
        analytics=analytics,
    ),
]
logging.info("Setting up Discord connection")
bot = Bot(
    bot_token=config.discord.bot_token,
    services=services,
    discord_status_settings=config.discord.status_message_settings,
    guild_id=config.discord.server_id,
    emoji_manager=emoji_manager,
)


# Set up Flask for webhooks
# flask_app = Flask(__name__)

def start():
    # Start Flask first (in separate thread)
    # logging.info("Starting Flask server")
    # flask_thread = threading.Thread(
    #    target=lambda: flask_app.run(host=host_name, port=port, debug=True, use_reloader=False))
    # flask_thread.start()

    # Connect the bot to Discord (last step, since it will block and trigger all the sub-services)
    bot.connect()


if __name__ == "__main__":
    start()
