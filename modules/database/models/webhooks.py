from modules.database.base.imports import *
from modules.utils import get_now_timestamp

from tautulli.tools.webhooks import TautulliWebhookTrigger


class Webhook(Base):
    __tablename__ = 'webhooks'
    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    webhook_type = Column("webhook_type", Enum(TautulliWebhookTrigger), nullable=False)
    created_at = Column("created_at", BigInteger, nullable=False, default=get_now_timestamp)
    updated_at = Column("updated_at", BigInteger, nullable=False, default=get_now_timestamp, onupdate=get_now_timestamp)

    def __init__(self, webhook_type: TautulliWebhookTrigger, **kwargs):
        self.webhook_type = webhook_type
        self.created_at = get_now_timestamp()
        self.updated_at = get_now_timestamp()
