from tautulli.tools.webhooks import TautulliWebhookTrigger

from modules.database.models.webhooks import Webhook as WebhookDatabaseModel
from modules.models._base import _Base


class Webhook(_Base):
    webhook_type: TautulliWebhookTrigger
    received_at: int

    @classmethod
    def from_database_record(cls, record: WebhookDatabaseModel) -> 'Webhook':
        return cls(
            webhook_type=record.webhook_type,
            received_at=record.created_at
        )
