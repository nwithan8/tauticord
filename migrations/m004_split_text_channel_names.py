import os
import shutil
from abc import ABC
from typing import Union

import yaml

from migrations.base import BaseMigration
from migrations.migration_names import V2_CONFIG_FILE, MIGRATION_004_CONFIG_FILE


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

    def remove_key_value_pair(self, key_path: list[Union[str, int]]):
        current = self._config

        for key in key_path[:-1]:
            if isinstance(key, int):
                # Trying to navigate to a specific index in a list
                if not current:
                    return

                if not isinstance(current, list):
                    raise Exception(f"Migration error. Expected a list, got {type(current)}")
                if key >= len(current):
                    return
                current = current[key]
            else:
                # Trying to navigate to a specific key in a dictionary
                if not current:
                    return

                if not isinstance(current, dict):
                    raise Exception(f"Migration error. Expected a dict, got {type(current)}")
                if key not in current:
                    return
                current = current[key]

        # Remove the key-value pair
        if isinstance(current, dict) and key_path[-1] in current:
            del current[key_path[-1]]

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
        self.new_config_file = f"{migration_data_directory}/{MIGRATION_004_CONFIG_FILE}"

    def announcements_channel_name_key_exists(self, file_path: str) -> bool:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

            path = ["Discord", "AnnouncementsChannelName"]

            return path_exists_in_yaml(yaml_data=data, path=path)

    def post_recently_added_message_key_exists(self, file_path: str) -> bool:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

            path = ["Discord", "PostRecentlyAddedMessage"]

            return path_exists_in_yaml(yaml_data=data, path=path)

    def summary_channel_name_key_exists(self, file_path: str) -> bool:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

            path = ["Discord", "SummaryChannelName"]

            return path_exists_in_yaml(yaml_data=data, path=path)

    def legacy_channel_name_key_exists(self, file_path: str) -> bool:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

            path = ["Discord", "ChannelName"]

            return path_exists_in_yaml(yaml_data=data, path=path)

    def pre_forward_check(self) -> bool:
        # Check if the old config file exists
        if not os.path.isfile(self.old_config_file):
            return False

        # If the file is already in the new schema, we don't need to do anything
        return not all([
            self.announcements_channel_name_key_exists(file_path=self.old_config_file),
            self.post_recently_added_message_key_exists(file_path=self.old_config_file),
            self.summary_channel_name_key_exists(file_path=self.old_config_file),
            not self.legacy_channel_name_key_exists(file_path=self.old_config_file),
        ])

    def forward(self):
        self.log("Renaming ChannelName to SummaryChannelName and adding AnnouncementsChannelName")

        with open(self.old_config_file, 'r') as f:
            old_config_data = yaml.safe_load(f)

            new_config = ConfigWriter(initial_data=old_config_data, config_file_path=self.new_config_file)

            # Rename ChannelName to SummaryChannelName
            legacy_channel_name = get_value_at_yaml_path(yaml_data=old_config_data, path=["Discord", "ChannelName"])
            new_config.add(value=legacy_channel_name,
                           key_path=["Discord", "SummaryChannelName"])
            new_config.remove_key_value_pair(key_path=["Discord", "ChannelName"])

            # Add AnnouncementsChannelName with an empty string value
            new_config.add(value="",
                           key_path=["Discord", "AnnouncementsChannelName"])
            # Add PostRecentlyAddedMessage with a default value
            new_config.add(value=False,
                           key_path=["Discord", "PostRecentlyAddedMessage"])

        # Write config file to disk
        new_config.save()

        # Copy/replace the old config file with the new one
        shutil.copy(self.new_config_file, self.old_config_file)

    def post_forward_check(self) -> bool:
        # Make sure the "old" config file has the new keys now
        return all([
            self.announcements_channel_name_key_exists(file_path=self.old_config_file),
            self.post_recently_added_message_key_exists(file_path=self.old_config_file),
            self.summary_channel_name_key_exists(file_path=self.old_config_file),
            not self.legacy_channel_name_key_exists(file_path=self.old_config_file)
        ])

    def pre_backwards_check(self) -> bool:
        return True

    def backwards(self):
        self.mark_undone()

    def post_backwards_check(self) -> bool:
        return True
