"""Conversation memory management."""
from typing import Dict
from langchain_community.chat_message_histories import ChatMessageHistory
from ..config import Settings
from ..utils.logger import get_logger

logger = get_logger()


class MemoryManager:
    """Manages conversation memory for different sessions."""

    def __init__(self, settings: Settings):
        """
        Initialize memory manager.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self._histories: Dict[str, ChatMessageHistory] = {}

    def get_history(self, session_id: str) -> ChatMessageHistory:
        """
        Get or create chat history for a session.

        Args:
            session_id: Session identifier

        Returns:
            Chat message history for the session
        """
        if session_id not in self._histories:
            logger.debug(f"📜 Creating new chat history for session: {session_id}")
            self._histories[session_id] = ChatMessageHistory()

        return self._histories[session_id]

    def add_user_message(self, session_id: str, message: str) -> None:
        """
        Add user message to history.

        Args:
            session_id: Session identifier
            message: User message
        """
        history = self.get_history(session_id)
        history.add_user_message(message)
        logger.debug(f"Added user message to session {session_id}")

    def add_ai_message(self, session_id: str, message: str) -> None:
        """
        Add AI message to history.

        Args:
            session_id: Session identifier
            message: AI message
        """
        history = self.get_history(session_id)
        history.add_ai_message(message)
        logger.debug(f"Added AI message to session {session_id}")

    def clear_history(self, session_id: str) -> None:
        """
        Clear history for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self._histories:
            self._histories[session_id].clear()
            logger.info(f"🗑️ Cleared history for session: {session_id}")
        else:
            logger.warning(f"⚠️ No history found for session: {session_id}")

    def clear_all(self) -> None:
        """Clear all session histories."""
        count = len(self._histories)
        self._histories.clear()
        logger.info(f"🗑️ Cleared all {count} session histories")

    def get_session_count(self) -> int:
        """Get number of active sessions."""
        return len(self._histories)
