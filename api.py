import argparse

from flask import (
    Flask,
)

import modules.logs as logging
from modules.errors import determine_exit_code
from consts import (
    DEFAULT_LOG_DIR,
    DEFAULT_DATABASE_PATH,
    CONSOLE_LOG_LEVEL,
    FILE_LOG_LEVEL,
    FLASK_ADDRESS,
    FLASK_PORT,
    FLASK_DATABASE_PATH,
)
from api.routes.index import index
from api.routes.webhooks.tautulli.index import webhooks_tautulli

APP_NAME = "API"

# Parse CLI arguments
parser = argparse.ArgumentParser(description="Tauticord API - API for Tauticord")
"""
Bot will use config, in order:
1. Explicit config file path provided as CLI argument, if included, or
2. Default config file path, if exists, or
3. Environmental variables
"""
parser.add_argument("-l", "--log", help="Log file directory", default=DEFAULT_LOG_DIR)
parser.add_argument("-d", "--database", help="Path to database file", default=DEFAULT_DATABASE_PATH)
args = parser.parse_args()


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
    logging.init(app_name=APP_NAME,
                 console_log_level=CONSOLE_LOG_LEVEL,
                 log_to_file=True,
                 log_file_dir=args.log,
                 file_log_level=FILE_LOG_LEVEL)


# Register Flask blueprints
application = Flask(APP_NAME)
application.config[FLASK_DATABASE_PATH] = args.database

application.register_blueprint(index)
application.register_blueprint(webhooks_tautulli)

if __name__ == "__main__":
    set_up_logging()

    application.run(host=FLASK_ADDRESS, port=FLASK_PORT, debug=False, use_reloader=False)
