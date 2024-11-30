from modules.database.base.imports import *

from modules.utils import get_now_timestamp


class RecentlyAddedItem(Base):
    __tablename__ = 'recently_added_items'
    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column("name", String, nullable=False)
    library_name = Column("library_name", String, nullable=False)
    webhook_id = Column("webhook_id", Integer, ForeignKey('webhooks.id'), nullable=False)
    created_at = Column("created_at", BigInteger, nullable=False, default=get_now_timestamp)
    updated_at = Column("updated_at", BigInteger, nullable=False, default=get_now_timestamp, onupdate=get_now_timestamp)

    def __init__(self, name: str, library_name: str, webhook_id: int, **kwargs):
        self.name = name
        self.library_name = library_name
        self.webhook_id = webhook_id
        self.created_at = get_now_timestamp()
        self.updated_at = get_now_timestamp()
