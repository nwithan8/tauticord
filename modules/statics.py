# Number 1-9, and A-Z
import subprocess
import sys

VERSION = "VERSIONADDEDBYGITHUB"
COPYRIGHT = "Copyright © YEARADDEDBYGITHUB Nate Harris. All rights reserved."
UNKNOWN_COMMIT_HASH = "unknown-commit"

CUSTOM_EMOJIS_FOLDER = "resources/emojis"

MONITORED_DISK_SPACE_FOLDER = "/monitor"

BOT_PREFIX = "tc-"
EMOJI_PREFIX = "tc"

MAX_EMBED_FIELD_NAME_LENGTH = 200  # 256 - estimated emojis + flairs + safety margin

KEY_RUN_ARGS_MONITOR_PATH = "run_args_monitor_path"
KEY_RUN_ARGS_CONFIG_PATH = "run_args_config_path"
KEY_RUN_ARGS_LOG_PATH = "run_args_log_path"

MAX_STREAM_COUNT = 20  # max number of emojis one user can post on a single message

ASCII_ART = """___________________  ______________________________________________ 
___  __/__    |_  / / /__  __/___  _/_  ____/_  __ \__  __ \__  __ \\
__  /  __  /| |  / / /__  /   __  / _  /    _  / / /_  /_/ /_  / / /
_  /   _  ___ / /_/ / _  /   __/ /  / /___  / /_/ /_  _, _/_  /_/ / 
/_/    /_/  |_\____/  /_/    /___/  \____/  \____/ /_/ |_| /_____/  
"""

INFO_SUMMARY = f"""Version: {VERSION}
"""


def get_sha_hash(sha: str) -> str:
    return f"git-{sha[0:7]}"


def get_last_commit_hash() -> str:
    """
    Get the seven character commit hash of the last commit.
    """
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except subprocess.SubprocessError:
        sha = UNKNOWN_COMMIT_HASH

    return get_sha_hash(sha)


def is_git() -> bool:
    return "GITHUB" in VERSION


def get_version() -> str:
    if not is_git():
        return VERSION

    return get_last_commit_hash()


def splash_logo() -> str:
    version = get_version()
    return f"""
{ASCII_ART}
Version {version}, Python {sys.version}

{COPYRIGHT}
"""
