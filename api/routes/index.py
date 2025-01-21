from flask import (
    Blueprint,
    request,
    Response as FlaskResponse,
)

from consts import (
    FLASK_POST,
    FLASK_GET,
)

index = Blueprint("index", __name__, url_prefix="")


@index.route("/ping", methods=[FLASK_GET])
def ping():
    return 'Pong!', 200


@index.route("/hello", methods=[FLASK_GET])
def hello_world():
    return 'Hello, World!', 200


@index.route("/health", methods=[FLASK_GET])
def health_check():
    return 'OK', 200
