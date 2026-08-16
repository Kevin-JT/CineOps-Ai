import logging
from typing import Any

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

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        client: httpx.AsyncClient,
        circuit_breaker: Any = None,
        timeout: float = 10.0,
    ) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._client = client
        self._circuit_breaker = circuit_breaker
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

        # Split message if it exceeds Telegram's 4096 character limit
        max_chunk_size = 4000
        chunks = [
            message[i : i + max_chunk_size]
            for i in range(0, len(message), max_chunk_size)
        ]

        for chunk in chunks:
            payload: dict[str, Any] = {
                "chat_id": self._chat_id,
                "text": chunk,
                "parse_mode": "Markdown",
            }

            async def _make_request(p: dict[str, Any]) -> httpx.Response:
                return await self._client.post(url, json=p, timeout=self._timeout)

            try:
                if self._circuit_breaker:
                    response = await self._circuit_breaker.call(
                        lambda p=payload: _make_request(p)
                    )
                else:
                    response = await _make_request(payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # If Markdown parsing failed (400 Bad Request), fallback to plain text!
                if e.response.status_code == 400:
                    logger.warning(
                        "Telegram Markdown parsing failed. Retrying in plain text..."
                    )
                    payload_plain = {
                        "chat_id": self._chat_id,
                        "text": chunk,
                    }
                    if self._circuit_breaker:
                        response = await self._circuit_breaker.call(
                            lambda p=payload_plain: _make_request(p)
                        )
                    else:
                        response = await _make_request(payload_plain)
                    response.raise_for_status()
                else:
                    raise

            data = response.json()
            if not data.get("ok"):
                error_msg = data.get("description", "Unknown Telegram Error")
                logger.error(f"Telegram API returned an error: {error_msg}")
                raise ProviderError(f"Telegram API error: {error_msg}")

        logger.info("Successfully sent message to Telegram.")
        return True
