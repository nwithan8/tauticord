from packaging.version import Version as PackagingVersion, parse as parse_version

import modules.database.repository as db


def initial_setup(database: db.DatabaseRepository):
    # Nothing needed for initial setup, will automatically create tables
    pass


MIGRATIONS = {
    # Above this version -> run migration
    "5.8.0": initial_setup,
}


def run_migrations(database_path: str) -> bool:
    database = db.DatabaseRepository(database_path=database_path)

    current_version = "0.0.0"
    try:
        current_version = database.get_database_version()
    except Exception as e:
        pass
    current_version = parse_version(version=current_version)

    for target_version_string, migration_function in MIGRATIONS.items():
        target_version: PackagingVersion = parse_version(version=target_version_string)
        if current_version < target_version:
            migration_function(database)
            if not database.set_database_version(version=target_version_string):
                print(f"Failed to set database version to {target_version_string}")
                return False

            print(f"Migration to version {target_version_string} complete")

    return True
