import os
import shutil
from abc import ABC
from typing import Union

import yaml

from migrations.base import BaseMigration
from migrations.migration_names import V2_CONFIG_FILE, MIGRATION_003_CONFIG_FILE


def json_to_yaml(json_data) -> str:
    return yaml.dump(json_data, default_flow_style=False, sort_keys=False)


def path_exists_in_yaml(yaml_data, path: list[str]) -> bool:
    current = yaml_data
    remaining_path = path.copy()
    for key in path:
        if remaining_path:
            remaining_path.pop(0)
        if isinstance(current, dict):
            if key not in current:  # Key not found in key-value pairs
                return False
            else:
                current = current[key]
        elif isinstance(current, list):
            if not isinstance(key, list):  # Key not configured properly
                return False
            else:
                for item in current:
                    return path_exists_in_yaml(yaml_data=item, path=remaining_path)
        else:
            return False
    return True


def get_value_at_yaml_path(yaml_data, path: list[str]) -> any:
    current = yaml_data
    remaining_path = path.copy()
    for key in path:
        if remaining_path:
            remaining_path.pop(0)
        if isinstance(current, dict):
            if key not in current:  # Key not found in key-value pairs
                return None
            else:
                current = current[key]
        elif isinstance(current, list):
            if not isinstance(key, int):  # Key not configured properly
                return None
            else:
                return get_value_at_yaml_path(yaml_data=current[key], path=remaining_path)
        else:
            return None
    return current


def path_ends_in_empty(yaml_data, path: list[str]) -> bool:
    if not path_exists_in_yaml(yaml_data=yaml_data, path=path):
        return False

    value_at_path = get_value_at_yaml_path(yaml_data=yaml_data, path=path)
    if value_at_path is None:
        return False

    return value_at_path == [] or value_at_path == {}


class ConfigWriter:
    def __init__(self, initial_data: dict, config_file_path: str):
        self._config = initial_data
        self._config_file_path = config_file_path

    def add(self, value, key_path: list[Union[str, int]]):
        current = self._config

        for key in key_path[:-1]:
            if isinstance(key, int):
                # Trying to navigate to a specific index in a list
                if not current:
                    current = []

                if not isinstance(current, list):
                    raise Exception(f"Migration error. Expected a list, got {type(current)}")
                if key >= len(current):
                    for _ in range(key - len(current) + 1):
                        current.append({})
                current = current[key]
            else:
                # Trying to navigate to a specific key in a dictionary
                if not current:
                    current = {}

                if not isinstance(current, dict):
                    raise Exception(f"Migration error. Expected a dict, got {type(current)}")
                if key not in current:
                    current[key] = {}
                current = current[key]

        current[key_path[-1]] = value

    def save(self):
        yaml_data = json_to_yaml(self._config)
        with open(self._config_file_path, 'w') as f:
            f.write(yaml_data)


class Migration(BaseMigration, ABC):
    def __init__(self, number: str, migration_data_directory: str, config_folder: str, logs_folder: str):
        super().__init__(number=number, migration_data_directory=migration_data_directory)
        self.config_folder = config_folder
        self.logs_folder = logs_folder
        self.old_config_file = f"{self.config_folder}/{V2_CONFIG_FILE}"
        self.new_config_file = f"{migration_data_directory}/{MIGRATION_003_CONFIG_FILE}"

    def recently_added_libraries_config_section_exists(self, file_path: str) -> bool:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

            path = ["Stats", "Libraries", "Libraries"]

            # If the Libraries section doesn't exist, that's an error that should be raised
            if not path_exists_in_yaml(yaml_data=data, path=path):
                path_string = " -> ".join(path)
                raise Exception(f"Missing {path_string} section in config file")

            # If the Libraries section is empty, that's fine
            if path_ends_in_empty(yaml_data=data, path=path):
                return True

            # Otherwise, confirm that the RecentlyAdded section is already in the config
            path = ["Stats", "Libraries", "Libraries", [], "RecentlyAdded", "Enable"]
            return path_exists_in_yaml(yaml_data=data, path=path)

    def recently_added_combined_libraries_config_section_exists(self, file_path: str) -> bool:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

            path = ["Stats", "Libraries", "CombinedLibraries"]

            # If the CombinedLibraries section doesn't exist, that's an error that should be raised
            if not path_exists_in_yaml(yaml_data=data, path=path):
                path_string = " -> ".join(path)
                raise Exception(f"Missing {path_string} section in config file")

            # If the CombinedLibraries section is empty, that's fine
            if path_ends_in_empty(yaml_data=data, path=path):
                return True

            # Otherwise, confirm that the RecentlyAdded section is already in the config
            path = ["Stats", "Libraries", "CombinedLibraries", [], "RecentlyAdded", "Enable"]
            return path_exists_in_yaml(yaml_data=data, path=path)

    def pre_forward_check(self) -> bool:
        # Check if the old config file exists
        if not os.path.isfile(self.old_config_file):
            return False

        # If the file is already in the new schema, we don't need to do anything
        if all([
            self.recently_added_libraries_config_section_exists(file_path=self.old_config_file),
            self.recently_added_combined_libraries_config_section_exists(file_path=self.old_config_file)
        ]):
            return False

        return True

    def forward(self):
        self.log("Adding RecentlyAdded section to Libraries and CombinedLibraries stats")

        with open(self.old_config_file, 'r') as f:
            old_config_data = yaml.safe_load(f)

            new_config = ConfigWriter(initial_data=old_config_data, config_file_path=self.new_config_file)

            # Recently Added
            stat_libraries: list[dict] = get_value_at_yaml_path(yaml_data=old_config_data,
                                                                path=["Stats", "Libraries", "Libraries"])
            stat_combined_libraries: list[dict] = get_value_at_yaml_path(yaml_data=old_config_data,
                                                                         path=["Stats", "Libraries",
                                                                               "CombinedLibraries"])

            # Need to add the RecentlyAdded section to each library in the Libraries section
            for i, _ in enumerate(stat_libraries or []):  # Will iterate 0 times if stat_libraries is None
                new_config.add(value={
                    "CustomName": "",
                    "CustomEmoji": "",
                    "Enable": False,
                    "VoiceChannelID": 0,
                    "Hours": 24,
                },
                    key_path=["Stats", "Libraries", "Libraries", i, "RecentlyAdded"])
            # Need to add the RecentlyAdded section to each library in the CombinedLibraries section
            for i, _ in enumerate(
                    stat_combined_libraries or []):  # Will iterate 0 times if stat_combined_libraries is None
                new_config.add(value={
                    "CustomName": "",
                    "CustomEmoji": "",
                    "Enable": False,
                    "VoiceChannelID": 0,
                    "Hours": 24,
                },
                    key_path=["Stats", "Libraries", "CombinedLibraries", i, "RecentlyAdded"])

        # Write config file to disk
        new_config.save()

        # Add YAML language server link at the top of the file
        with open(self.new_config_file, 'r') as f:
            data = f.read()
        with open(self.new_config_file, 'w') as f:
            f.write(
                "# yaml-language-server: $schema=https://raw.githubusercontent.com/nwithan8/tauticord/master/.schema/config_v2.schema.json\n\n")
            f.write(data)

        # Copy/replace the old config file with the new one
        shutil.copy(self.new_config_file, self.old_config_file)

    def post_forward_check(self) -> bool:
        # Make sure the "old" config file has the "RecentlyAdded" section now
        return all([
            self.recently_added_libraries_config_section_exists(file_path=self.old_config_file),
            self.recently_added_combined_libraries_config_section_exists(file_path=self.old_config_file)
        ])

    def pre_backwards_check(self) -> bool:
        return True

    def backwards(self):
        self.mark_undone()

    def post_backwards_check(self) -> bool:
        return True
