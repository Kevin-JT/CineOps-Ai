import logging
import re

from src.domain.interfaces import TranscriptEntry, TranscriptProvider
from src.domain.models.clip import (
    ClipIntelligenceResult,
    ClipSegment,
    ClipVerificationStatus,
)
from src.domain.models.recommendation import ContentStrategy
from src.domain.models.youtube import YouTubeSource

logger = logging.getLogger(__name__)


def seconds_to_timestamp(seconds: float) -> str:
    """Converts seconds into MM:SS or HH:MM:SS format."""
    total_sec = max(0, round(seconds))
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def timestamp_to_seconds(ts: str) -> float:
    """Parses MM:SS or HH:MM:SS timestamp string into total seconds."""
    parts = list(map(int, ts.split(":")))
    if len(parts) == 3:
        return float(parts[0] * 3600 + parts[1] * 60 + parts[2])
    if len(parts) == 2:
        return float(parts[0] * 60 + parts[1])
    return 0.0


class ClipIntelligenceService:
    """
    Domain service responsible for clip intelligence, scene matching, timestamp discovery, and clip quality scoring.
    """

    def __init__(
        self,
        transcript_provider: TranscriptProvider | None = None,
        buffer_seconds: int = 5,
        min_duration_seconds: int = 10,
        max_duration_seconds: int = 45,
    ) -> None:
        self.transcript_provider = transcript_provider
        self.buffer_seconds = buffer_seconds
        self.min_duration_seconds = min_duration_seconds
        self.max_duration_seconds = max_duration_seconds

    async def analyze_clip(
        self,
        youtube_source: YouTubeSource,
        content_strategy: ContentStrategy | None = None,
    ) -> ClipIntelligenceResult:
        """
        Analyzes available YouTube source evidence and produces a ClipIntelligenceResult.
        Guarantees NO fabricated timestamps when timing evidence is unavailable.
        """
        transcript_entries: list[TranscriptEntry] | None = None
        if self.transcript_provider:
            try:
                transcript_entries = await self.transcript_provider.get_transcript(
                    youtube_source.video_id
                )
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    f"Transcript retrieval failed for video '{youtube_source.video_id}': {e}"
                )

        if transcript_entries and content_strategy:
            clips = self._analyze_transcript(
                youtube_source=youtube_source,
                content_strategy=content_strategy,
                entries=transcript_entries,
            )
            if clips:
                clips.sort(
                    key=lambda c: (c.clip_score, c.confidence_score), reverse=True
                )
                return ClipIntelligenceResult(
                    best_clip=clips[0],
                    alternative_clips=clips[1:3],
                    transcript_available=True,
                )

        # Fallback for unverified clip intelligence when transcript timing evidence is missing
        hook_text = (
            content_strategy.video_hook if content_strategy else youtube_source.title
        )
        unverified_clip = ClipSegment(
            source_video_id=youtube_source.video_id,
            source_url=youtube_source.url,
            scene_description=f"Key moment from '{youtube_source.title}' matching short-form strategy.",
            match_reason=f"Source metadata strongly matches video hook: '{hook_text}'.",
            clip_score=round(min(youtube_source.relevance_score, 75.0), 1),
            confidence_score=45.0,
            verification_status=ClipVerificationStatus.UNVERIFIED,
            timestamp_verified=False,
            start_timestamp=None,
            end_timestamp=None,
            duration_seconds=None,
        )

        return ClipIntelligenceResult(
            best_clip=unverified_clip,
            alternative_clips=[],
            transcript_available=False,
        )

    def _analyze_transcript(
        self,
        youtube_source: YouTubeSource,
        content_strategy: ContentStrategy,
        entries: list[TranscriptEntry],
    ) -> list[ClipSegment]:
        """
        Extracts candidate clip segments from transcript timing evidence.
        """
        clips: list[ClipSegment] = []
        keywords = re.findall(r"\w+", content_strategy.video_hook.lower())
        relevant_entries = []

        for idx, entry in enumerate(entries):
            text_lower = entry.text.lower()
            match_count = sum(1 for kw in keywords if kw in text_lower and len(kw) > 3)
            if match_count > 0:
                relevant_entries.append((idx, match_count))

        if not relevant_entries:
            return clips

        for idx, _match_count in relevant_entries[:3]:
            entry = entries[idx]
            raw_start = max(0.0, entry.start - self.buffer_seconds)
            raw_end = entry.start + entry.duration + self.buffer_seconds
            duration = round(raw_end - raw_start)

            if duration < self.min_duration_seconds:
                raw_end = raw_start + self.min_duration_seconds
                duration = self.min_duration_seconds
            elif duration > self.max_duration_seconds:
                raw_end = raw_start + self.max_duration_seconds
                duration = self.max_duration_seconds

            start_ts = seconds_to_timestamp(raw_start)
            end_ts = seconds_to_timestamp(raw_end)

            clip_score = min(100.0, 70.0 + (youtube_source.relevance_score * 0.30))

            clips.append(
                ClipSegment(
                    source_video_id=youtube_source.video_id,
                    source_url=youtube_source.url,
                    scene_description=f"Dialogue moment: '{entry.text}'",
                    match_reason=f"Transcript dialogue directly matches video hook: '{content_strategy.video_hook}'.",
                    clip_score=round(clip_score, 1),
                    confidence_score=92.0,
                    verification_status=ClipVerificationStatus.VERIFIED,
                    timestamp_verified=True,
                    start_timestamp=start_ts,
                    end_timestamp=end_ts,
                    duration_seconds=duration,
                )
            )

        return clips
