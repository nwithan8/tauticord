from tautulli.tools.webhooks import TautulliWebhook

from modules.database.database import RootDatabase
from modules.database.models.recently_added_item import RecentlyAddedItem as RecentlyAddedItemDatabaseModel
from modules.database.models.version import Version as VersionDatabaseModel
from modules.database.models.webhooks import Webhook as WebhookDatabaseModel
from modules.models import RecentlyAddedItem as RecentlyAddedItemModel, Webhook as WebhookModel
from modules.webhooks import RecentlyAddedWebhook, RecentlyAddedWebhookData

"""
NOTES:
- `database.py` deals with raw database records and ORM models.
- `repository.py` translates database records/query results into in-memory models. 
    - No function calling a repository function should ever receive back a raw database record.
"""


class DatabaseRepository:
    def __init__(self, database_path: str):
        self._database = RootDatabase(sqlite_file=database_path)

    def get_database_version(self) -> str:
        """
        Get the version of the database

        :return: The version of the database
        """
        try:
            version: VersionDatabaseModel = self._database.get_version()
            return version.semver
        except Exception as e:
            raise Exception(f'Error getting database version: {e}') from e

    def set_database_version(self, version: str) -> bool:
        """
        Set the version of the database

        :param version: The version to set
        :type version: str
        :return: True if the version was set, False otherwise
        """
        try:
            return self._database.set_version(semver=version)
        except Exception as e:
            raise Exception(f'Error setting database version: {e}')

    def add_received_recently_added_webhook_to_database(self, webhook: RecentlyAddedWebhook) -> WebhookModel | None:
        """
        Add a received recently-added webhook to the database

        :param webhook: The webhook to add
        :type webhook: TautulliWebhook
        :return: The webhook that was added, or None if the webhook could not be added
        """
        try:
            database_entry: WebhookDatabaseModel = self._database.add_webhook(webhook_type=webhook.trigger)
            data: RecentlyAddedWebhookData = webhook.data  # type: ignore
            library_name = data.library_name
            item_name = data.title
            _ = self.add_recently_added_item_to_database(webhook=database_entry,
                                                         library_name=library_name,
                                                         item_name=item_name)

            return WebhookModel.from_database_record(record=database_entry)
        except Exception as e:
            raise Exception(f'Error adding webhook to database: {e}') from e

    def add_recently_added_item_to_database(self, webhook: WebhookDatabaseModel, library_name: str,
                                            item_name: str) -> RecentlyAddedItemModel | None:
        """
        Add a "recently added" item to the database

        :param webhook: The webhook that triggered the item
        :type webhook: Webhook
        :param library_name: The name of the library the item was added to
        :type library_name: str
        :param item_name: The name of the item that was added
        :type item_name: str
        :return: The "recently added" item that was added, or None if the item could not be added
        """
        try:
            database_entry: RecentlyAddedItemDatabaseModel = (
                self._database.add_recently_added_item(
                    name=item_name,
                    library_name=library_name,
                    webhook_id=webhook.id)
            )
            return RecentlyAddedItemModel.from_database_record(record=database_entry)
        except Exception as e:
            raise Exception(f'Error adding recently added item to database: {e}')

    def get_all_recently_added_items_in_past_x_minutes_for_libraries(self, minutes: int, library_names: list[str]) -> \
            list[RecentlyAddedItemModel]:
        """
        Get all "recently added" items in the past x minutes for specific libraries

        :param minutes: The number of minutes to look back
        :type minutes: int
        :param library_names: The names of the libraries to filter by
        :type library_names: list[str]
        :return: A list of "recently added" items in the past x minutes for specific libraries
        """
        try:
            database_entries: list[RecentlyAddedItemDatabaseModel] = (
                self._database.get_all_recently_added_items_in_past_x_minutes_for_libraries(
                    minutes=minutes,
                    library_names=library_names)
            )
            return [RecentlyAddedItemModel.from_database_record(record=entry) for entry in database_entries]
        except Exception as e:
            raise Exception(f'Error getting webhooks from database: {e}') from e
