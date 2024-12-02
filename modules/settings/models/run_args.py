from typing import Optional

from modules.settings.models.base import BaseConfig


class RunArgs(BaseConfig):
    performance_disk_space_mapping: Optional[str] = None
    log_path: Optional[str] = None
    config_path: Optional[str] = None
    database_path: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "log_path": self.log_path,
            "config_path": self.config_path,
            "database_path": self.database_path,
            "performance_disk_space_mapping": self.performance_disk_space_mapping,
        }
