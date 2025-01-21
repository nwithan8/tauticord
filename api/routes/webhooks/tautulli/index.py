from flask import (
    Blueprint,
    request as flask_request,
    Response as FlaskResponse,
    current_app,
)

from api.controllers.webhook_processor import WebhookProcessor
from consts import (
    FLASK_POST,
    FLASK_GET,
    FLASK_DATABASE_PATH,
)

webhooks_tautulli = Blueprint("tautulli", __name__, url_prefix="/webhooks/tautulli")


@webhooks_tautulli.route("/recently_added", methods=[FLASK_POST])
def tautulli_webhook():
    database_path = current_app.config[FLASK_DATABASE_PATH]
    return WebhookProcessor.process_tautulli_recently_added_webhook(request=flask_request,
                                                                    database_path=database_path)
