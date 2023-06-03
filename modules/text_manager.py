from typing import Dict, Any, Union

from modules import statics, utils
from modules.emojis import EmojiManager


class TextManager:
    """
    Manages text formatting and anonymization.
    """
    def __init__(self, anon_rules: Dict[str, Any]) -> None:
        self._anon_rules: dict = anon_rules
        self._anon_hide_usernames: bool = anon_rules.get(statics.KEY_HIDE_USERNAMES, False)
        self._anon_hide_player_names: bool = anon_rules.get(statics.KEY_HIDE_PLAYER_NAMES, False)
        self._anon_hide_platforms: bool = anon_rules.get(statics.KEY_HIDE_PLATFORMS, False)
        self._anon_hide_quality: bool = anon_rules.get(statics.KEY_HIDE_QUALITY, False)
        self._anon_hide_bandwidth: bool = anon_rules.get(statics.KEY_HIDE_BANDWIDTH, False)
        self._anon_hide_transcoding: bool = anon_rules.get(statics.KEY_HIDE_TRANSCODING, False)
        self._anon_hide_progress: bool = anon_rules.get(statics.KEY_HIDE_PROGRESS, False)
        self._anon_hide_eta: bool = anon_rules.get(statics.KEY_HIDE_ETA, False)

    def _session_user_message(self, session, emoji_manager: EmojiManager) -> Union[str, None]:
        if self._anon_hide_usernames:
            return None

        emoji = emoji_manager.get_emoji(key="person")
        username = session.username
        stub = f"""{emoji} **{username}**"""

        return stub

    def _session_player_message(self, session, emoji_manager: EmojiManager) -> Union[str, None]:
        if self._anon_hide_platforms and self._anon_hide_player_names:
            return None

        emoji = emoji_manager.get_emoji(key="device")
        player = None if self._anon_hide_player_names else session.player
        product = None if self._anon_hide_platforms else session.product

        stub = f"""{emoji}"""
        if player is not None:
            stub += f""" **{player}**"""
            # Only optionally show product if player is shown.
            if product is not None:
                stub += f""" ({product})"""

        return stub

    def _session_details_message(self, session, emoji_manager: EmojiManager) -> Union[str, None]:
        if self._anon_hide_quality and self._anon_hide_bandwidth and self._anon_hide_transcoding:
            return None

        quality_profile = None if self._anon_hide_quality else session.quality_profile
        bandwidth = None if self._anon_hide_bandwidth else session.bandwidth
        transcoding = None if self._anon_hide_transcoding else session.transcoding_stub

        emoji = emoji_manager.get_emoji(key="resolution")
        stub = f"""{emoji}"""
        if quality_profile is not None:
            stub += f""" **{quality_profile}**"""
            # Only optionally show bandwidth if quality profile is shown.
            if bandwidth is not None:
                stub += f""" ({bandwidth})"""
        if transcoding is not None:
            stub += f"""{transcoding}"""

        return stub

    def _session_progress_message(self, session, emoji_manager: EmojiManager) -> Union[str, None]:
        if self._anon_hide_progress:
            return None

        emoji = emoji_manager.get_emoji(key="progress")
        progress = session.progress_marker
        stub = f"""{emoji} **{progress}**"""
        if not self._anon_hide_eta:
            eta = session.eta
            stub += f""" (ETA: {eta})"""

        return stub

    def session_title(self, session, session_number: int, emoji_manager: EmojiManager) -> str:
        emoji = emoji_manager.emoji_from_stream_number(number=session_number)
        icon = session.get_status_icon(emoji_manager=emoji_manager)
        media_type_icon = session.get_type_icon(emoji_manager=emoji_manager)
        title = session.title
        return f"""{emoji} | {icon} {media_type_icon} *{title}*"""

    def session_body(self, session, emoji_manager: EmojiManager) -> str:
        user_message = self._session_user_message(session=session, emoji_manager=emoji_manager)
        player_message = self._session_player_message(session=session, emoji_manager=emoji_manager)
        details_message = self._session_details_message(session=session, emoji_manager=emoji_manager)
        progress_message = self._session_progress_message(session=session, emoji_manager=emoji_manager)

        stubs = [user_message, player_message, details_message, progress_message]
        stubs = [stub for stub in stubs if stub is not None]
        return "\n".join(stubs)

    def overview_footer(self, no_connection: bool, activity, emoji_manager: EmojiManager, add_termination_tip: bool) -> str:
        if no_connection or activity is None:
            return "**Connection lost.**"

        if activity.stream_count == 0:
            return "**No active sessions.**"

        stream_count = activity.stream_count
        stream_count_word = utils.make_plural(word='stream', count=stream_count)
        overview_message = f"""{stream_count} {stream_count_word}"""

        if activity.transcode_count > 0 and not self._anon_hide_transcoding:
            transcode_count = activity.transcode_count
            transcode_count_word = utils.make_plural(word='transcode', count=transcode_count)
            overview_message += f""" ({transcode_count} {transcode_count_word})"""

        if activity.total_bandwidth and not self._anon_hide_bandwidth:
            bandwidth_emoji = emoji_manager.get_emoji(key='bandwidth')
            bandwidth = activity.total_bandwidth
            overview_message += f""" @ {bandwidth_emoji} {bandwidth}"""
            if activity.lan_bandwidth:
                lan_bandwidth_emoji = emoji_manager.get_emoji(key='home')
                lan_bandwidth = activity.lan_bandwidth
                overview_message += f""" {lan_bandwidth_emoji} {lan_bandwidth}"""

        if add_termination_tip:
            overview_message += f"\n\nTo terminate a stream, react with the stream number."

        return overview_message
