from tautulli.tools.webhooks import TautulliWebhookTrigger

import modules.database.base.base as db
from modules.database.models.webhooks import Webhook
from modules.utils import get_minutes_ago_timestamp


class RootDatabase(db.SQLAlchemyDatabase):
    def __init__(self,
                 sqlite_file: str):
        super().__init__(sqlite_file=sqlite_file)
        Webhook.__table__.create(bind=self.engine, checkfirst=True)

    def add_webhook(self, webhook_type: TautulliWebhookTrigger) -> None | object:
        """
        Add a webhook to the database
        :param webhook_type: The type of webhook to add
        :type webhook_type: TautulliWebhookTrigger
        :return: The webhook that was added
        """
        try:
            return self._create_entry(table_schema=Webhook, webhook_type=webhook_type)
        except:
            raise Exception("Failed to add webhook to database")

    def get_all_webhooks_by_type(self, webhook_type: TautulliWebhookTrigger) -> list[Webhook]:
        """
        Get all webhooks by type
        :param webhook_type: The type of webhook to get
        :type webhook_type: TautulliWebhookTrigger
        :return: A list of webhooks of the specified type
        """
        try:
            return self._get_all_entries(Webhook, (Webhook.webhook_type == webhook_type))  # type: ignore
        except:
            raise Exception("Failed to get webhooks from database")

    def get_all_webhooks_by_time(self, minutes: int) -> list[Webhook]:
        """
        Get all webhooks by time
        :param minutes: The number of minutes to look back
        :type minutes: int
        :return: A list of webhooks received in the past x minutes
        """
        timestamp = get_minutes_ago_timestamp(minutes=minutes)
        try:
            return self._get_all_entries(Webhook, (Webhook.created_at >= timestamp))  # type: ignore
        except:
            raise Exception("Failed to get webhooks from database")

    def get_all_webhooks_by_type_and_time(self, webhook_type: TautulliWebhookTrigger, minutes: int) -> list[Webhook]:
        """
        Get all webhooks by type and time
        :param webhook_type: The type of webhook to get
        :type webhook_type: TautulliWebhookTrigger
        :param minutes: The number of minutes to look back
        :type minutes: int
        :return: A list of webhooks of the specified type received in the past x minutes
        """
        timestamp = get_minutes_ago_timestamp(minutes=minutes)
        try:
            return self._get_all_entries(Webhook, (Webhook.webhook_type == webhook_type), (Webhook.created_at >= timestamp))  # type: ignore
        except:
            raise Exception("Failed to get webhooks from database")
