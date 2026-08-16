from src.domain.models.performance import PerformanceMetrics
from src.domain.services.performance_analyzer import PerformanceAnalyzer


def test_performance_analyzer_insufficient_data() -> None:
    analyzer = PerformanceAnalyzer(min_samples=3)

    records = [
        PerformanceMetrics(
            recommendation_id="r1", platform="instagram", views=1000, likes=100
        ),
        PerformanceMetrics(
            recommendation_id="r2", platform="youtube", views=2000, likes=200
        ),
    ]

    result = analyzer.analyze_performance(records)
    assert result.has_enough_data is False
    assert result.sample_size == 2
    assert result.confidence == "Low"
    assert "Not enough performance data yet" in result.insights[0]


def test_performance_analyzer_sufficient_data() -> None:
    analyzer = PerformanceAnalyzer(min_samples=3)

    records = [
        PerformanceMetrics(
            recommendation_id="r1", platform="instagram", views=1000, likes=100
        ),
        PerformanceMetrics(
            recommendation_id="r2", platform="instagram", views=2000, likes=300
        ),
        PerformanceMetrics(
            recommendation_id="r3", platform="youtube", views=5000, likes=500
        ),
    ]

    result = analyzer.analyze_performance(records)
    assert result.has_enough_data is True
    assert result.sample_size == 3
    assert result.confidence == "Low"
    assert "PERFORMANCE INSIGHTS:" in result.formatted_summary
    assert "Instagram" in result.formatted_summary
    assert "YouTube" in result.formatted_summary


def test_performance_analyzer_high_confidence() -> None:
    analyzer = PerformanceAnalyzer(min_samples=3)

    records = [
        PerformanceMetrics(
            recommendation_id=f"r_{i}",
            platform="tiktok" if i % 2 == 0 else "instagram",
            views=1000 * (i + 1),
            likes=100 * (i + 1),
        )
        for i in range(16)
    ]

    result = analyzer.analyze_performance(records)
    assert result.has_enough_data is True
    assert result.sample_size == 16
    assert result.confidence == "High"
    assert "16" in result.insights[0]
