import httpx
import pytest
import respx

from src.core.exceptions import ProviderError
from src.infrastructure.providers.telegram_provider import TelegramProvider


@pytest.fixture
def provider() -> TelegramProvider:
    return TelegramProvider(bot_token="bot123", chat_id="chat456", timeout=1.0)


@pytest.mark.asyncio
@respx.mock
async def test_telegram_send_success(provider: TelegramProvider) -> None:
    url = f"{provider.BASE_URL}bot123/sendMessage"

    route = respx.post(url).mock(return_value=httpx.Response(200, json={"ok": True}))

    result = await provider.send_message("Hello World")

    assert route.called
    assert result is True


@pytest.mark.asyncio
@respx.mock
async def test_telegram_send_failure(provider: TelegramProvider) -> None:
    url = f"{provider.BASE_URL}bot123/sendMessage"

    respx.post(url).mock(
        return_value=httpx.Response(
            200, json={"ok": False, "description": "Chat not found"}
        )
    )

    with pytest.raises(ProviderError, match="Telegram API error: Chat not found"):
        await provider.send_message("Hello World")


@pytest.mark.asyncio
async def test_telegram_missing_config() -> None:
    provider = TelegramProvider(bot_token="", chat_id="")
    with pytest.raises(ProviderError, match="configuration missing"):
        await provider.send_message("prompt")
