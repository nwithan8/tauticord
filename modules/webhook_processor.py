from typing import Union

from flask import (
    jsonify,
    request as flask_request,
)

from modules.discord.bot import Bot
from modules.tautulli.webhooks import TautulliWebhook, TautulliWebhookTrigger


class WebhookProcessor:
    def __init__(self):
        pass

    @staticmethod
    def process_tautulli_webhook(request: flask_request, bot: Bot) -> [Union[str, None], int]:
        """
        Process a Discord-compatible webhook from Tautulli.
        Return an empty response and a 200 status code back to Tautulli as confirmation.
        """
        webhook: TautulliWebhook = TautulliWebhook.from_flask_request(request=request)
        trigger: TautulliWebhookTrigger = webhook.trigger if webhook else None

        return jsonify({}), 200
