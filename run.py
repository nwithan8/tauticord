import argparse
import os
import threading

from flask import (
    Flask,
    request as flask_request,
)
from pydantic import ValidationError as PydanticValidationError

import modules.logs as logging
import modules.tautulli.tautulli_connector as tautulli
from consts import (
    GOOGLE_ANALYTICS_ID,
    APP_NAME,
    DEFAULT_CONFIG_PATH,
    DEFAULT_LOG_DIR,
    DEFAULT_DATABASE_PATH,
    CONSOLE_LOG_LEVEL,
    FILE_LOG_LEVEL,
    FLASK_ADDRESS,
    FLASK_PORT,
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
from modules.errors import determine_exit_code, TauticordMigrationFailure, TauticordSetupFailure
from modules.settings.config_parser import Config
from modules.statics import (
    splash_logo,
    MONITORED_DISK_SPACE_FOLDER,
    KEY_RUN_ARGS_CONFIG_PATH,
    KEY_RUN_ARGS_LOG_PATH,
    KEY_RUN_ARGS_MONITOR_PATH,
    KEY_RUN_ARGS_DATABASE_PATH,
)
from modules.webhook_processor import WebhookProcessor
from modules.database.migrations import run_migrations as run_database_migrations_steps

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
parser.add_argument("-d", "--database", help="Path to database file", default=DEFAULT_DATABASE_PATH)
parser.add_argument("-u", "--usage", help="Path to directory to monitor for disk usage",
                    default=MONITORED_DISK_SPACE_FOLDER)
args = parser.parse_args()

config_directory = os.path.dirname(args.config)
if config_directory == "":
    config_directory = "./"


def run_with_potential_exit_on_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.fatal(f"Fatal error occurred. Shutting down: {e}")
            exit_code = determine_exit_code(exception=e)
            logging.fatal(f"Exiting with code {exit_code}")
            exit(exit_code)

    return wrapper


@run_with_potential_exit_on_error
def set_up_logging():
    logging.init(app_name=APP_NAME, console_log_level=CONSOLE_LOG_LEVEL, log_to_file=True, log_file_dir=args.log,
                 file_log_level=FILE_LOG_LEVEL)
    logging.info(splash_logo())


@run_with_potential_exit_on_error
def run_config_migrations() -> None:
    # Run configuration migrations
    migration_manager = MigrationManager(
        migration_data_directory=os.path.join(config_directory, "migration_data"),
        config_directory=config_directory,
        logs_directory=args.log)
    if not migration_manager.run_migrations():
        raise TauticordMigrationFailure("Migrations failed.")


@run_with_potential_exit_on_error
def run_database_migrations(database_path: str) -> None:
    # Run database migrations
    if not run_database_migrations_steps(database_path=database_path):
        raise TauticordMigrationFailure("Database migrations failed.")


@run_with_potential_exit_on_error
def set_up_configuration() -> Config:
    # Set up configuration
    kwargs = {
        KEY_RUN_ARGS_MONITOR_PATH: args.usage,
        KEY_RUN_ARGS_CONFIG_PATH: config_directory,
        KEY_RUN_ARGS_LOG_PATH: args.log,
        KEY_RUN_ARGS_DATABASE_PATH: args.database,
    }
    try:
        return Config(config_path=f"{args.config}", **kwargs)
    except PydanticValidationError as e:  # Redirect Pydantic validation errors during config parsing
        raise TauticordSetupFailure(f"Configuration error: {e}")


@run_with_potential_exit_on_error
def set_up_analytics(config: Config) -> GoogleAnalytics:
    # Set up analytics
    return GoogleAnalytics(analytics_id=GOOGLE_ANALYTICS_ID,
                           anonymous_ip=True,
                           do_not_track=not config.extras.allow_analytics)


@run_with_potential_exit_on_error
def set_up_tautulli_connection(config: Config,
                               analytics: GoogleAnalytics,
                               database_path: str) -> tautulli.TautulliConnector:
    # Set up Tautulli connection
    return tautulli.TautulliConnector(
        tautulli_settings=config.tautulli,
        display_settings=config.display,
        stats_settings=config.stats,
        database_path=database_path,
        analytics=analytics,
    )


@run_with_potential_exit_on_error
def set_up_emoji_manager() -> EmojiManager:
    # Set up emoji manager
    return EmojiManager()


@run_with_potential_exit_on_error
def set_up_discord_bot(config: Config,
                       tautulli_connector: tautulli.TautulliConnector,
                       emoji_manager: EmojiManager,
                       analytics: GoogleAnalytics) -> Bot:
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
    return Bot(
        bot_token=config.discord.bot_token,
        services=services,
        discord_status_settings=config.discord.status_message_settings,
        guild_id=config.discord.server_id,
        emoji_manager=emoji_manager,
    )


@run_with_potential_exit_on_error
def start_api(config: Config, discord_bot: Bot, database_path: str) -> [Flask, threading.Thread]:
    api = Flask(APP_NAME)

    @api.route('/ping', methods=['GET'])
    def ping():
        return 'Pong!', 200

    @api.route('/hello', methods=['GET'])
    def hello_world():
        return 'Hello, World!', 200

    @api.route('/health', methods=['GET'])
    def health_check():
        return 'OK', 200

    @api.route('/webhooks/tautulli', methods=['POST'])
    def tautulli_webhook():
        return WebhookProcessor.process_tautulli_webhook(request=flask_request,
                                                         bot=discord_bot,
                                                         database_path=database_path)

    flask_thread = threading.Thread(
        target=lambda: api.run(host=FLASK_ADDRESS, port=FLASK_PORT, debug=True, use_reloader=False))
    logging.info("Starting Flask server")
    flask_thread.start()

    return api, flask_thread


@run_with_potential_exit_on_error
def start(discord_bot: Bot) -> None:
    # Connect the bot to Discord (last step, since it will block and trigger all the sub-services)
    discord_bot.connect()


if __name__ == "__main__":
    set_up_logging()
    run_config_migrations()
    run_database_migrations(database_path=args.database)
    _config: Config = set_up_configuration()
    _analytics: GoogleAnalytics = set_up_analytics(config=_config)
    _emoji_manager: EmojiManager = set_up_emoji_manager()
    _tautulli_connector: tautulli.TautulliConnector = set_up_tautulli_connection(config=_config,
                                                                                 analytics=_analytics,
                                                                                 database_path=args.database)
    _discord_bot: Bot = set_up_discord_bot(config=_config,
                                           tautulli_connector=_tautulli_connector,
                                           emoji_manager=_emoji_manager,
                                           analytics=_analytics)
    _api, _flask_thread = start_api(config=_config, discord_bot=_discord_bot, database_path=args.database)
    start(discord_bot=_discord_bot)
