import logging
from typing import Any

import httpx

from src.core.exceptions import ProviderError
from src.core.retry import async_retry
from src.domain.interfaces import AIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    Provider for Google's Gemini API.
    Generates recommendations based on prompts.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    DEFAULT_MODEL = "gemini-1.5-flash"

    def __init__(
        self,
        api_key: str,
        client: httpx.AsyncClient,
        model: str = DEFAULT_MODEL,
        circuit_breaker: Any = None,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._client = client
        self._model = model
        self._circuit_breaker = circuit_breaker
        self._timeout = timeout

    @async_retry(
        exceptions=(httpx.RequestError, httpx.HTTPStatusError),
        raise_exc=ProviderError,
    )
    async def generate_recommendations(self, prompt: str) -> str:
        """
        Sends a prompt to the Gemini API and returns the generated text.

        Args:
            prompt: The instruction prompt for the AI.

        Returns:
            The generated string response.

        Raises:
            ProviderError: If the API request fails or the API key is missing.
        """
        if not self._api_key:
            logger.warning(
                "Gemini API key is missing. Cannot generate recommendations."
            )
            raise ProviderError("Gemini API key not configured")

        url = f"{self.BASE_URL}/{self._model}:generateContent"
        params = {"key": self._api_key}

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        }

        headers = {"Content-Type": "application/json"}

        async def _make_request() -> httpx.Response:
            return await self._client.post(
                url, params=params, headers=headers, json=payload, timeout=self._timeout
            )

        if self._circuit_breaker:
            response = await self._circuit_breaker.call(_make_request)
        else:
            response = await _make_request()

        response.raise_for_status()
        data = response.json()

        # Extract text from Gemini response structure
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                raise ProviderError("No candidates returned from Gemini")

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            if not parts:
                raise ProviderError("No text parts returned from Gemini")

            text_response = str(parts[0].get("text", ""))
            logger.info("Successfully generated content from Gemini.")
            return text_response

        except (IndexError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            raise ProviderError(f"Invalid Gemini response format: {e}") from e
