import pytest
from pydantic import ValidationError

from src.domain.models.performance import PerformanceMetrics


def test_performance_metrics_valid() -> None:
    metrics = PerformanceMetrics(
        recommendation_id="rec_123",
        platform="instagram",
        views=1000,
        likes=100,
        comments=10,
        shares=5,
        saves=5,
    )
    assert metrics.recommendation_id == "rec_123"
    assert metrics.platform == "instagram"
    assert metrics.views == 1000
    assert metrics.engagement_rate == 12.0  # (100+10+5+5)/1000 * 100
    assert metrics.comment_rate == 1.0  # 10/1000 * 100
    assert metrics.share_rate == 0.5  # 5/1000 * 100
    assert metrics.like_rate == 10.0  # 100/1000 * 100


def test_performance_metrics_missing_optional() -> None:
    metrics = PerformanceMetrics(
        recommendation_id="rec_123",
        platform="youtube",
        views=500,
        likes=50,
    )
    assert metrics.comments is None
    assert metrics.shares is None
    assert metrics.engagement_rate == 10.0  # (50)/500 * 100
    assert metrics.comment_rate is None
    assert metrics.share_rate is None


def test_performance_metrics_zero_views() -> None:
    metrics = PerformanceMetrics(
        recommendation_id="rec_123",
        platform="tiktok",
        views=0,
        likes=0,
    )
    assert metrics.engagement_rate is None
    assert metrics.comment_rate is None
    assert metrics.like_rate is None


def test_performance_metrics_negative_views_invalid() -> None:
    with pytest.raises(ValidationError):
        PerformanceMetrics(
            recommendation_id="rec_123",
            platform="instagram",
            views=-10,
        )


def test_performance_metrics_invalid_platform() -> None:
    with pytest.raises(ValidationError):
        PerformanceMetrics(
            recommendation_id="rec_123",
            platform="myspace",  # type: ignore[arg-type]
            views=100,
        )
