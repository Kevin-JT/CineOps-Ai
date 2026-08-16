from unittest.mock import AsyncMock

import pytest

from src.domain.interfaces import TranscriptEntry
from src.domain.models.ai_response import OnScreenText
from src.domain.models.clip import ClipVerificationStatus
from src.domain.models.recommendation import ContentStrategy
from src.domain.models.youtube import YouTubeSource
from src.domain.services.clip_intelligence import (
    ClipIntelligenceService,
    seconds_to_timestamp,
    timestamp_to_seconds,
)


def make_youtube_source() -> YouTubeSource:
    return YouTubeSource(
        video_id="v123",
        title="Interstellar Docking Scene",
        channel_name="MovieClips",
        url="https://youtube.com/watch?v=v123",
        relevance_score=90.0,
        quality_score=85.0,
    )


def make_content_strategy() -> ContentStrategy:
    return ContentStrategy(
        video_hook="No, it's necessary.",
        on_screen_text=OnScreenText(
            opening="Docking sequence", middle="Spinning station", ending="Success"
        ),
        editing_instructions="Cut on beat",
        caption="Epic docking scene",
        hashtags=["#interstellar", "#sci-fi", "#cinema", "#space", "#movie"],
        first_comment="Unbelievable scene!",
    )


def test_timestamp_conversions() -> None:
    assert seconds_to_timestamp(192.5) == "03:12"
    assert seconds_to_timestamp(3805.0) == "01:03:25"
    assert timestamp_to_seconds("03:12") == 192.0
    assert timestamp_to_seconds("01:03:25") == 3805.0


@pytest.mark.asyncio
async def test_clip_intelligence_verified_transcript() -> None:
    transcript_provider_mock = AsyncMock()
    transcript_provider_mock.get_transcript.return_value = [
        TranscriptEntry(
            text="Cooper, we are lining up with the endurance.",
            start=180.0,
            duration=5.0,
        ),
        TranscriptEntry(text="It's impossible!", start=188.0, duration=3.0),
        TranscriptEntry(text="No, it's necessary.", start=192.0, duration=4.0),
    ]

    service = ClipIntelligenceService(transcript_provider=transcript_provider_mock)
    source = make_youtube_source()
    strategy = make_content_strategy()

    result = await service.analyze_clip(source, content_strategy=strategy)

    assert result.transcript_available is True
    best = result.best_clip
    assert best.timestamp_verified is True
    assert best.verification_status == ClipVerificationStatus.VERIFIED
    assert best.start_timestamp is not None
    assert best.end_timestamp is not None
    assert best.duration_seconds is not None
    assert best.clip_score > 80.0
    assert "necessary" in best.scene_description.lower()


@pytest.mark.asyncio
async def test_clip_intelligence_unverified_missing_transcript_no_fake_timestamps() -> (
    None
):
    transcript_provider_mock = AsyncMock()
    transcript_provider_mock.get_transcript.return_value = None

    service = ClipIntelligenceService(transcript_provider=transcript_provider_mock)
    source = make_youtube_source()
    strategy = make_content_strategy()

    result = await service.analyze_clip(source, content_strategy=strategy)

    assert result.transcript_available is False
    best = result.best_clip
    # Absolute critical requirement: NO FABRICATED TIMESTAMPS!
    assert best.timestamp_verified is False
    assert best.verification_status == ClipVerificationStatus.UNVERIFIED
    assert best.start_timestamp is None
    assert best.end_timestamp is None
    assert best.duration_seconds is None
    assert best.confidence_score == 45.0


@pytest.mark.asyncio
async def test_clip_intelligence_transcript_error_graceful_fallback() -> None:
    transcript_provider_mock = AsyncMock()
    transcript_provider_mock.get_transcript.side_effect = RuntimeError("Network error")

    service = ClipIntelligenceService(transcript_provider=transcript_provider_mock)
    source = make_youtube_source()

    result = await service.analyze_clip(source, content_strategy=None)

    assert result.transcript_available is False
    best = result.best_clip
    assert best.timestamp_verified is False
    assert best.verification_status == ClipVerificationStatus.UNVERIFIED
    assert best.start_timestamp is None
