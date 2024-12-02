from abc import abstractmethod
from datetime import datetime

import modules.logs as logging


def _marker(undone: bool = False) -> str:
    marker = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if undone:
        marker += " - UNDONE"

    return marker


class BaseMigration:
    def __init__(self, number: str, migration_data_directory: str):
        self.number = number
        self.migration_data_directory = migration_data_directory
        self._migration_file = f"{migration_data_directory}/.migration_{self.number}"

    def log(self, message: str):
        logging.info(f"Migration {self.number}: {message}")

    def error(self, message: str):
        logging.error(f"Migration {self.number}: {message}")

    @abstractmethod
    def pre_forward_check(self) -> bool:
        """
        Check if the forward migration needs to run
        """
        return True

    @abstractmethod
    def forward(self):
        """
        Run the forward migration
        """
        pass

    @abstractmethod
    def post_forward_check(self) -> bool:
        """
        Check if the forward migration was successful
        """
        return True

    @abstractmethod
    def pre_backwards_check(self) -> bool:
        """
        Check if the backwards migration needs to run
        """
        return True

    @abstractmethod
    def backwards(self):
        """
        Run the backwards migration
        """
        pass

    @abstractmethod
    def post_backwards_check(self) -> bool:
        """
        Check if the backwards migration was successful
        """
        return True

    def mark_done(self):
        """
        Mark the migration as done
        """
        with open(self._migration_file, 'a') as f:
            f.write(f"{_marker()}\n")

    def mark_undone(self):
        """
        Mark the migration as undone
        """
        with open(self._migration_file, 'a') as f:
            f.write(f"{_marker(undone=True)}\n")
