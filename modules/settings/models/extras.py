from modules.settings.models.base import BaseConfig


class Extras(BaseConfig):
    allow_analytics: bool
    update_reminders: bool

    def as_dict(self) -> dict:
        return {
            "allow_analytics": self.allow_analytics,
            "update_reminders": self.update_reminders,
        }
