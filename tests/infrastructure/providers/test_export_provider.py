import json
from pathlib import Path

import pytest

from src.domain.models.media_item import MediaItem
from src.domain.models.recommendation import Recommendation
from src.infrastructure.providers.export_provider import LocalExportProvider


@pytest.mark.asyncio
async def test_export_recommendation(tmp_path: Path) -> None:
    service = LocalExportProvider(output_dir=str(tmp_path))

    item = MediaItem(
        id="1", title="Test Movie", overview="Overview", media_type="movie"
    )
    rec = Recommendation(
        id="rec_1",
        items=[item],
        target_audience="General",
        reasoning="Reason",
        viral_score=95.0,
    )

    await service.export_recommendation(rec)

    json_file = tmp_path / "recommendation.json"
    md_file = tmp_path / "recommendation.md"

    assert json_file.exists()
    assert md_file.exists()

    data = json.loads(json_file.read_text())
    assert data["id"] == "rec_1"

    md_content = md_file.read_text()
    assert "Test Movie" in md_content
    assert "95.0/100" in md_content
