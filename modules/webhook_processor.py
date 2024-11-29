from typing import Union

from flask import (
    jsonify,
    request as flask_request,
)
from tautulli.tools.webhooks import DiscordWebhook

from modules.discord.bot import Bot
import modules.database.repository as db


class WebhookProcessor:
    def __init__(self):
        pass

    @staticmethod
    def process_tautulli_webhook(request: flask_request, bot: Bot, database_path: str) -> [Union[str, None], int]:
        """
        Process a Discord-compatible webhook from Tautulli.
        Return an empty response and a 200 status code back to Tautulli as confirmation.
        """
        webhook: DiscordWebhook = DiscordWebhook.from_flask_request(request=request)

        database = db.DatabaseRepository(database_path=database_path)
        database.add_received_webhook_to_database(webhook=webhook)

        return jsonify({}), 200
