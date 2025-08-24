import enum


class AnnouncementMessageType(enum.Enum):
    RECENTLY_ADDED_POSTERS = 1

    @classmethod
    def get_footer(cls, announcement_message_type: 'AnnouncementMessageType') -> str:
        footer_prefix = "Announcement Type:"
        if announcement_message_type == cls.RECENTLY_ADDED_POSTERS:
            return f"{footer_prefix} Recently Added Carousel"
        raise ValueError(f"Invalid announcement message type: {announcement_message_type}")
