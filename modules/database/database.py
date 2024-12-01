from tautulli.tools.webhooks import TautulliWebhookTrigger

import modules.database.base.base as db
from modules.database.models.recently_added_item import RecentlyAddedItem
from modules.database.models.version import Version
from modules.database.models.webhooks import Webhook
from modules.utils import get_minutes_ago_timestamp


class RootDatabase(db.SQLAlchemyDatabase):
    def __init__(self,
                 sqlite_file: str):
        super().__init__(sqlite_file=sqlite_file)
        Version.__table__.create(bind=self.engine, checkfirst=True)
        Webhook.__table__.create(bind=self.engine, checkfirst=True)
        RecentlyAddedItem.__table__.create(bind=self.engine, checkfirst=True)

    # Version table

    def get_version(self) -> Version:
        """
        Get the version of the database
        :return: The version of the database
        """
        try:
            return self._get_first_entry(Version) # type: ignore
        except Exception as e:
            raise Exception("Failed to get version from database") from e

    def set_version(self, semver: str) -> bool:
        """
        Set the version of the database
        :param semver: The version to set
        :type semver: str
        :return: True if the version was set, False otherwise
        """
        try:
            entry = self.get_version()
            if not entry:
                return self._create_entry(table_schema=Version, semver=semver) is not None  # type: ignore
            else:
                return self._update_entry_single_field(entry=entry, field_name="semver", field_value=semver)  # type: ignore
        except Exception as e:
            raise Exception("Failed to set version in database") from e

    # Webhooks table

    def add_webhook(self, webhook_type: TautulliWebhookTrigger) -> None | Webhook:
        """
        Add a webhook to the database
        :param webhook_type: The type of webhook to add
        :type webhook_type: TautulliWebhookTrigger
        :return: The webhook that was added
        """
        try:
            return self._create_entry(table_schema=Webhook, webhook_type=webhook_type) # type: ignore
        except Exception as e:
            raise Exception("Failed to add webhook to database") from e

    def get_all_webhooks_by_type(self, webhook_type: TautulliWebhookTrigger) -> list[Webhook]:
        """
        Get all webhooks by type
        :param webhook_type: The type of webhook to get
        :type webhook_type: TautulliWebhookTrigger
        :return: A list of webhooks of the specified type
        """
        try:
            return self._get_all_entries(Webhook,(Webhook.webhook_type == webhook_type))  # type: ignore
        except Exception as e:
            raise Exception("Failed to get webhooks from database") from e

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
        except Exception as e:
            raise Exception("Failed to get webhooks from database") from e

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
            return self._get_all_entries(Webhook,
                                         (Webhook.webhook_type == webhook_type),
                                         (Webhook.created_at >= timestamp))  # type: ignore
        except Exception as e:
            raise Exception("Failed to get webhooks from database") from e

    # RecentlyAddedItem table

    def add_recently_added_item(self, name: str, library_name: str, webhook_id: int) -> None | RecentlyAddedItem:
        """
        Add a recently added item to the database
        :param name: The name of the item
        :type name: str
        :param library_name: The name of the library
        :type library_name: str
        :param webhook_id: The ID of the webhook
        :type webhook_id: int
        :return: The recently added item that was added
        """
        try:
            return self._create_entry(table_schema=RecentlyAddedItem,
                                      name=name,
                                      library_name=library_name,
                                      webhook_id=webhook_id) # type: ignore
        except Exception as e:
            raise Exception("Failed to add recently added item to database") from e

    def get_all_recently_added_items_in_past_x_minutes(self, minutes: int) -> list[RecentlyAddedItem]:
        """
        Get all recently added items received in the past x minutes
        :param minutes: The number of minutes to look back
        :type minutes: int
        :return: A list of recently added items received in the past x minutes
        """
        timestamp = get_minutes_ago_timestamp(minutes=minutes)
        try:
            return self._get_all_entries(RecentlyAddedItem, (RecentlyAddedItem.created_at >= timestamp))  # type: ignore
        except Exception as e:
            raise Exception("Failed to get recently added items from database") from e

    def get_all_recently_added_items_in_past_x_minutes_for_libraries(self, minutes: int, library_names: list[str]) -> list[RecentlyAddedItem]:
        """
        Get all recently added items in the past x minutes for specific libraries
        :param minutes: The number of minutes to look back
        :type minutes: int
        :param library_names: The names of the libraries to filter by
        :type library_names: list[str]
        :return: A list of recently added items in the past x minutes for specific libraries
        """
        timestamp = get_minutes_ago_timestamp(minutes=minutes)
        try:
            return self._get_all_entries(RecentlyAddedItem,
                                         (RecentlyAddedItem.created_at >= timestamp),
                                         (RecentlyAddedItem.library_name.in_(library_names)))  # type: ignore
        except Exception as e:
            raise Exception("Failed to get recently added items from database") from e
