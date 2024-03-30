from datetime import datetime

import modules.logs as logging


def _marker(undone: bool = False) -> str:
    marker = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if undone:
        marker += " - UNDONE"

    return marker


class BaseMigration:
    def __init__(self, number: str, migration_tracker_folder: str):
        self.number = number
        self._migration_file = f"{migration_tracker_folder}/.migration_{self.number}"

    def log(self, message: str):
        logging.info(f"Migration {self.number}: {message}")

    def error(self, message: str):
        logging.error(f"Migration {self.number}: {message}")

    def pre_forward_check(self) -> bool:
        """
        Check if the forward migration needs to run
        """
        return True

    def forward(self):
        """
        Run the forward migration
        """
        pass

    def post_forward_check(self) -> bool:
        """
        Check if the forward migration was successful
        """
        return True

    def pre_backwards_check(self) -> bool:
        """
        Check if the backwards migration needs to run
        """
        return True

    def backwards(self):
        """
        Run the backwards migration
        """
        pass

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
