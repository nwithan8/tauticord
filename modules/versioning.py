import asyncio
from typing import Union

import objectrest

import modules.logs as logging
from consts import (
    GITHUB_REPO,
    GITHUB_REPO_MASTER_BRANCH
)
from modules.statics import (
    get_version,
    is_git,
    get_sha_hash,
)


def _get_latest_github_release() -> Union[str, None]:
    logging.info('Retrieving latest version information from GitHub')

    url = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'
    data = objectrest.get_json(url)

    return data.get('tag_name', None)  # "tag_name" is the version number (e.g. 2.0.0), not the "name" (e.g. "v2.0.0")


def _newer_github_release_available(current_version: str) -> bool:
    latest_version = _get_latest_github_release()
    if latest_version is None:
        return False

    return latest_version != current_version


def _get_latest_github_commit() -> Union[str, None]:
    logging.info('Retrieving latest commit information from GitHub')

    url = f'https://api.github.com/repos/{GITHUB_REPO}/commits/{GITHUB_REPO_MASTER_BRANCH}'
    data = objectrest.get_json(url)
    sha: Union[str, None] = data.get('sha', None)

    if not sha:
        return None

    return get_sha_hash(sha=sha)


def _newer_github_commit_available(current_commit_hash: str) -> bool:
    latest_commit = _get_latest_github_commit()
    if latest_commit is None:
        return False

    return latest_commit != current_commit_hash


def newer_version_available() -> bool:
    current_version = get_version()
    if is_git():
        return _newer_github_commit_available(current_commit_hash=current_version)
    else:
        return _newer_github_release_available(current_version=current_version)


class VersionChecker:
    def __init__(self, enable: bool):
        self.enable = enable
        self._new_version_available = False

    async def check_for_new_version(self):
        while True:
            try:
                self._new_version_available = newer_version_available()
                if self._new_version_available:
                    logging.debug(f"New version available")
                await asyncio.sleep(60 * 60)  # Check for new version every hour
            except Exception:
                exit(1)  # Die on any unhandled exception for this subprocess (i.e. internet connection loss)

    def is_new_version_available(self) -> bool:
        if not self.enable:
            return False

        return self._new_version_available
