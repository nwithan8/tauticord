from typing import Union

from flask import (
    jsonify,
    request as flask_request,
)
import modules.logs as logging

import modules.database.repository as db
from modules.webhooks import RecentlyAddedWebhook


class WebhookProcessor:
    def __init__(self):
        pass

    @staticmethod
    def process_tautulli_recently_added_webhook(request: flask_request, database_path: str) -> [Union[str, None], int]:
        """
        Process a configured recently-added webhook from Tautulli.
        Return an empty response and a 200 status code back to Tautulli as confirmation.
        """
        webhook: RecentlyAddedWebhook = RecentlyAddedWebhook.from_flask_request(request=request)

        if webhook:
            database = db.DatabaseRepository(database_path=database_path)
            _ = database.add_received_recently_added_webhook_to_database(webhook=webhook)
        else:
            logging.debug("Received invalid recently-added webhook from Tautulli")

        return jsonify({}), 200
