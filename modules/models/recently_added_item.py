from modules.database.models.recently_added_item import RecentlyAddedItem as RecentlyAddedItemDatabaseModel
from modules.models._base import _Base


class RecentlyAddedItem(_Base):
    name: str
    library_name: str
    added_at: int

    @classmethod
    def from_database_record(cls, record: RecentlyAddedItemDatabaseModel) -> 'RecentlyAddedItem':
        return cls(
            name=record.name,
            library_name=record.library_name,
            added_at=record.created_at
        )
