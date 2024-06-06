import enum
import re
from typing import Union

from tautulli.tools.webhooks import DiscordWebhookIngestor

from consts import WEBHOOK_TRIGGER_PATTERN


class TautulliWebhookTrigger(enum.Enum):
    PLAYBACK_START = "on_play"
    PLAYBACK_STOP = "on_stop"
    PLAYBACK_PAUSE = "on_pause"
    PLAYBACK_RESUME = "on_resume"
    PLAYBACK_ERROR = "on_error"
    TRANSCODE_DECISION_CHANGE = "on_change"
    INTRO_MARKER = "on_intro"
    COMMERCIAL_MARKER = "on_commercial"
    CREDITS_MARKER = "on_credits"
    WATCHED = "on_watched"
    BUFFER_WARNING = "on_buffer"
    USER_CONCURRENT_STREAMS = "on_concurrent"
    USER_NEW_DEVICE = "on_newdevice"
    RECENTLY_ADDED = "on_created"
    PLEX_SERVER_DOWN = "on_intdown"
    PLEX_SERVER_UP = "on_intup"
    PLEX_REMOTE_ACCESS_DOWN = "on_extdown"
    PLEX_REMOTE_ACCESS_UP = "on_extup"
    PLEX_UPDATE_AVAILABLE = "on_pmsupdate"
    TAUTULLI_UPDATE_AVAILABLE = "on_plexpyupdate"
    TAUTULLI_DATABASE_CORRUPT = "on_plexpydbcorrupt"

    @classmethod
    def from_string(cls, trigger: str) -> Union["TautulliWebhookTrigger", None]:
        """
        Get a Tautulli webhook trigger from a string.
        """
        for t in cls:
            if t.value == trigger:
                return t
        return None

    def __str__(self):
        return self.value


class TautulliWebhook:
    def __init__(self, data: DiscordWebhookIngestor, trigger: TautulliWebhookTrigger):
        self._data: DiscordWebhookIngestor = data
        self.trigger: TautulliWebhookTrigger = trigger

    @staticmethod
    def parse_trigger(text: str) -> Union[TautulliWebhookTrigger, None]:
        """
        Parse a Tautulli webhook trigger from a string.
        """
        if not text:
            return None

        match = re.search(WEBHOOK_TRIGGER_PATTERN, text)

        if not match:
            return None

        trigger = match.group(1)
        return TautulliWebhookTrigger.from_string(trigger=trigger)

    @classmethod
    def from_flask_request(cls, request) -> Union["TautulliWebhook", None]:
        """
        Parse a Tautulli webhook from a Flask request.
        """
        try:
            webhook_data: DiscordWebhookIngestor = DiscordWebhookIngestor.from_flask_request(request=request)
        except Exception as e:
            # Parse error due to Pydantic validation error
            return None

        # Can't parse webhook data from incoming request
        if not webhook_data or not webhook_data.data or not webhook_data.data.content:
            return None

        webhook_trigger = cls.parse_trigger(text=webhook_data.data.content)

        # Can't parse trigger from webhook data
        if not webhook_trigger:
            return None

        return cls(data=webhook_data, trigger=webhook_trigger)
