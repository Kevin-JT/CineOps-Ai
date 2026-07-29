import logging

import httpx

from src.core.exceptions import ProviderError
from src.core.retry import async_retry
from src.domain.interfaces import NotificationProvider

logger = logging.getLogger(__name__)


class TelegramProvider(NotificationProvider):
    """
    Provider for Telegram Bot API.
    Sends notifications and messages to a specific chat.
    """

    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, bot_token: str, chat_id: str, timeout: float = 10.0) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._timeout = timeout

    @async_retry(
        exceptions=(httpx.RequestError, httpx.HTTPStatusError),
        raise_exc=ProviderError,
    )
    async def send_message(self, message: str) -> bool:
        """
        Sends a text message to the configured Telegram chat.

        Args:
            message: The content to send.

        Returns:
            True if the message was sent successfully.

        Raises:
            ProviderError: If the API request fails.
        """
        if not self._bot_token or not self._chat_id:
            logger.warning(
                "Telegram bot token or chat ID missing. Cannot send message."
            )
            raise ProviderError("Telegram configuration missing")

        url = f"{self.BASE_URL}{self._bot_token}/sendMessage"

        payload = {
            "chat_id": self._chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            if not data.get("ok"):
                error_msg = data.get("description", "Unknown Telegram Error")
                logger.error(f"Telegram API returned an error: {error_msg}")
                raise ProviderError(f"Telegram API error: {error_msg}")

            logger.info("Successfully sent message to Telegram.")
            return True
