from tautulli.tools.webhooks import DiscordWebhook, TautulliWebhookTrigger

from modules.database.database import RootDatabase
from modules.database.models.webhooks import Webhook


class DatabaseRepository:
    def __init__(self, database_path: str):
        self._database = RootDatabase(sqlite_file=database_path)

    def add_received_webhook_to_database(self, webhook: DiscordWebhook) -> bool:
        """
        Add a received webhook to the database

        :param webhook: The webhook to add
        :type webhook: DiscordWebhook
        :return: True if the webhook was added, False otherwise
        """
        try:
            _ = self._database.add_webhook(webhook_type=webhook.trigger)
            return True
        except Exception as e:
            print(f'Error adding webhook to database: {e}')
            return False

    def get_all_recently_added_webhooks_in_past_x_minutes(self, minutes: int) -> list[Webhook]:
        """
        Get all "recently added" webhooks received in the past x minutes

        :param minutes: The number of minutes to look back
        :type minutes: int
        :return: A list of "recently added" webhooks received in the past x minutes
        """
        try:
            return self._database.get_all_webhooks_by_type_and_time(webhook_type=TautulliWebhookTrigger.RECENTLY_ADDED,
                                                                    minutes=minutes)
        except Exception as e:
            print(f'Error getting webhooks from database: {e}')
            return []
