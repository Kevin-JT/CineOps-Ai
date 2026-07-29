import httpx
import pytest
import respx

from src.core.exceptions import ProviderError
from src.infrastructure.providers.gemini_provider import GeminiProvider


@pytest.fixture
def provider() -> GeminiProvider:
    return GeminiProvider(api_key="test_key", timeout=1.0)


@pytest.mark.asyncio
@respx.mock
async def test_gemini_generate_success(provider: GeminiProvider) -> None:
    mock_data = {
        "candidates": [
            {"content": {"parts": [{"text": "This is a generated recommendation."}]}}
        ]
    }

    url = f"{provider.BASE_URL}/{provider.DEFAULT_MODEL}:generateContent?key=test_key"
    route = respx.post(url).mock(return_value=httpx.Response(200, json=mock_data))

    result = await provider.generate_recommendations("Give me a rec")

    assert route.called
    assert result == "This is a generated recommendation."


@pytest.mark.asyncio
@respx.mock
async def test_gemini_generate_invalid_format(provider: GeminiProvider) -> None:
    # Missing candidates
    respx.post(
        f"{provider.BASE_URL}/{provider.DEFAULT_MODEL}:generateContent?key=test_key"
    ).mock(return_value=httpx.Response(200, json={"other": "data"}))

    with pytest.raises(ProviderError, match="No candidates returned"):
        await provider.generate_recommendations("prompt")


@pytest.mark.asyncio
async def test_gemini_missing_api_key() -> None:
    provider = GeminiProvider(api_key="")
    with pytest.raises(ProviderError, match="not configured"):
        await provider.generate_recommendations("prompt")
