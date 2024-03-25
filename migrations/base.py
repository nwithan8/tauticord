class BaseMigration:
    def __init__(self, number: str, migration_file: str):
        self._number = number
        self._migration_file = migration_file

    def log(self, message: str):
        print(f"Migration {self._number}: {message}")

    def forward(self):
        pass

    def backwards(self):
        pass

    def mark_done(self):
        with open(self._migration_file, 'a') as f:
            f.write(f"{self._number}\n")

    def mark_undone(self):
        with open(self._migration_file, 'r') as f:
            lines = f.readlines()

        with open(self._migration_file, 'w') as f:
            for line in lines:
                if line.strip() != self._number:
                    f.write(line)
