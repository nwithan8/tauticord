import modules.logs as logging
from modules.emojis import EmojiManager
from modules.tautulli.models.session import Session
from modules.text_manager import TextManager


class TautulliStreamInfo:
    def __init__(self, session: Session, session_number: int):
        self._session = session
        self._session_number = session_number

    def get_title(self, emoji_manager: EmojiManager, text_manager: TextManager) -> str:
        try:
            return text_manager.session_title(session=self._session, session_number=self._session_number,
                                              emoji_manager=emoji_manager)
        except Exception as title_exception:
            logging.error(str(title_exception))
            return "Unknown"

    def get_body(self, emoji_manager: EmojiManager, text_manager: TextManager) -> str:
        try:
            return text_manager.session_body(session=self._session, emoji_manager=emoji_manager)
        except Exception as body_exception:
            logging.error(str(body_exception))
            return f"Could not display data for session {self._session_number}"
