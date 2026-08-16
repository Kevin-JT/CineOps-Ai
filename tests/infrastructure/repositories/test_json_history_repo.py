import json
from pathlib import Path

import pytest

from src.domain.models.media_item import MediaItem
from src.domain.models.performance import PerformanceMetrics
from src.infrastructure.repositories.json_repo import JsonHistoryRepository


@pytest.mark.asyncio
async def test_json_history_repo_atomic_save_and_performance(tmp_path: Path) -> None:
    storage_file = tmp_path / "storage.json"
    repo = JsonHistoryRepository(file_path=str(storage_file))

    item = MediaItem(
        id="m_1",
        title="Inception",
        overview="Dream within a dream",
        media_type="movie",
        rating=8.8,
        popularity=90.0,
    )
    await repo.save(item)

    metrics = PerformanceMetrics(
        recommendation_id="rec_m_1",
        platform="instagram",
        views=5000,
        likes=500,
        comments=40,
    )
    await repo.save_performance(metrics)

    assert storage_file.exists()

    # Re-instantiate repo to test loading from disk
    repo2 = JsonHistoryRepository(file_path=str(storage_file))
    assert await repo2.exists("m_1")

    perf_records = await repo2.get_all_performance()
    assert len(perf_records) == 1
    assert perf_records[0].recommendation_id == "rec_m_1"
    assert perf_records[0].views == 5000


@pytest.mark.asyncio
async def test_json_history_repo_backward_compatibility(tmp_path: Path) -> None:
    storage_file = tmp_path / "legacy_storage.json"

    legacy_data = {
        "m_old": {
            "id": "m_old",
            "title": "Old Movie",
            "overview": "Classic",
            "media_type": "movie",
            "rating": 7.5,
            "popularity": 40.0,
        }
    }
    storage_file.write_text(json.dumps(legacy_data), encoding="utf-8")

    repo = JsonHistoryRepository(file_path=str(storage_file))
    assert await repo.exists("m_old")

    perf_records = await repo.get_all_performance()
    assert perf_records == []
