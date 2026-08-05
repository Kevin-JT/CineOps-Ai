import httpx
import pytest
import respx

from src.core.exceptions import ProviderError
from src.infrastructure.providers.gemini_provider import GeminiProvider


@pytest.fixture
def provider() -> GeminiProvider:
    return GeminiProvider(api_key="test_key", client=httpx.AsyncClient(), timeout=1.0)


@pytest.mark.asyncio
@respx.mock
async def test_gemini_generate_success(provider: GeminiProvider) -> None:
    mock_data = {
        "candidates": [
            {"content": {"parts": [{"text": "This is a generated recommendation."}]}}
        ]
    }

    url = f"{provider.BASE_URL}/{provider.DEFAULT_MODEL}:generateContent"
    route = respx.post(url).mock(return_value=httpx.Response(200, json=mock_data))

    result = await provider.generate_recommendations("Give me a rec")

    assert route.called
    assert result == "This is a generated recommendation."


@pytest.mark.asyncio
@respx.mock
async def test_gemini_generate_invalid_format(provider: GeminiProvider) -> None:
    # Missing candidates
    respx.post(f"{provider.BASE_URL}/{provider.DEFAULT_MODEL}:generateContent").mock(
        return_value=httpx.Response(200, json={"other": "data"})
    )

    with pytest.raises(ProviderError, match="No candidates returned"):
        await provider.generate_recommendations("prompt")


@pytest.mark.asyncio
async def test_gemini_missing_api_key() -> None:
    provider = GeminiProvider(api_key="", client=httpx.AsyncClient())
    with pytest.raises(ProviderError, match="not configured"):
        await provider.generate_recommendations("prompt")


@pytest.mark.asyncio
@respx.mock
async def test_gemini_missing_text_parts(provider: GeminiProvider) -> None:
    # Missing parts array
    respx.post(f"{provider.BASE_URL}/{provider.DEFAULT_MODEL}:generateContent").mock(
        return_value=httpx.Response(200, json={"candidates": [{"content": {}}]})
    )
    with pytest.raises(ProviderError, match="No text parts returned"):
        await provider.generate_recommendations("prompt")


@pytest.mark.asyncio
@respx.mock
async def test_gemini_parse_exception(provider: GeminiProvider) -> None:
    # Intentionally malformed structure to trigger IndexError or KeyError
    respx.post(f"{provider.BASE_URL}/{provider.DEFAULT_MODEL}:generateContent").mock(
        return_value=httpx.Response(
            200, json={"candidates": [{"content": {"parts": []}}]}
        )
    )
    with pytest.raises(ProviderError, match="No text parts returned"):
        await provider.generate_recommendations("prompt")


@pytest.mark.asyncio
@respx.mock
async def test_gemini_with_circuit_breaker() -> None:
    from src.core.circuit_breaker import CircuitBreaker

    cb = CircuitBreaker("test_cb", failure_threshold=2)
    provider = GeminiProvider(
        api_key="test_key", client=httpx.AsyncClient(), circuit_breaker=cb
    )

    mock_data = {"candidates": [{"content": {"parts": [{"text": "cb success"}]}}]}
    route = respx.post(
        f"{provider.BASE_URL}/{provider.DEFAULT_MODEL}:generateContent"
    ).mock(return_value=httpx.Response(200, json=mock_data))

    result = await provider.generate_recommendations("prompt")
    assert result == "cb success"
    assert route.called
