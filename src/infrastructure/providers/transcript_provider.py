import logging

import httpx

from src.domain.interfaces import TranscriptEntry, TranscriptProvider

logger = logging.getLogger(__name__)


class YouTubeTranscriptProvider(TranscriptProvider):
    """
    Infrastructure provider for retrieving public YouTube video transcript data.
    Gracefully returns None if transcripts are unavailable or disabled.
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self.client = client or httpx.AsyncClient(timeout=10.0)

    async def get_transcript(self, video_id: str) -> list[TranscriptEntry] | None:
        try:
            url = (
                f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en&fmt=json3"
            )
            response = await self.client.get(url)
            if response.status_code != 200:
                return None

            data = response.json()
            events = data.get("events", [])
            entries: list[TranscriptEntry] = []

            for ev in events:
                t_start_ms = ev.get("tStartMs", 0)
                d_duration_ms = ev.get("dDurationMs", 0)
                segs = ev.get("segs", [])
                text = "".join(s.get("utf8", "") for s in segs if "utf8" in s).strip()
                if text:
                    entries.append(
                        TranscriptEntry(
                            text=text,
                            start=round(t_start_ms / 1000.0, 2),
                            duration=round(d_duration_ms / 1000.0, 2),
                        )
                    )

            return entries if entries else None
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Transcript unavailable for video {video_id}: {e}")
            return None
