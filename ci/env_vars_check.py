import re

# Check if all environment variables defined in config_parser.py are documented

class File:
    def __init__(self, file_name: str, prefix: str = "", suffix: str = ""):
        self.file_name = file_name
        self.prefix = prefix
        self.suffix = suffix

    def element_to_find(self, element: str):
        return f"{self.prefix}{element}{self.suffix}"

if __name__ == "__main__":
    config_parser = open("modules/config_parser.py").read()
    env_name_overrides = re.findall(r"env_name_override\s?=\s?['\"]([A-Z0-9_]*)['\"]\)", config_parser)
    print("Found the following environment variables:")
    print(env_name_overrides)

    to_check = [File("README.md", prefix="| "), File("templates/tauticord.xml", prefix="Target=\"")]
    results = {}
    for file in to_check:
        results[file.file_name] = []
        for env_name_override in env_name_overrides:
            if file.element_to_find(element=env_name_override) not in open(file.file_name).read():
                results[file.file_name].append(env_name_override)

    failed = False
    for file in to_check:
        if len(results[file.file_name]) > 0:
            print(f"The following environment variables are not noted in {file.file_name}:")
            print(results[file.file_name])
            failed = True

    if failed:
        exit(1)

    print("All environment variables are documented.")
    exit(0)
