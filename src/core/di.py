import httpx
from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource

from src.application.services.caption import CaptionGenerationService
from src.application.services.coordinator import WorkflowCoordinator
from src.application.services.hashtag import HashtagGenerationService
from src.application.services.prompt_builder import PromptBuilder
from src.application.services.recommendation import RecommendationService
from src.application.services.trending import TrendingService
from src.config.settings import Settings, get_settings
from src.core.circuit_breaker import CircuitBreaker
from src.domain.services.deduplication import DeduplicationService
from src.domain.services.filtering import MediaFilterService
from src.domain.services.ranking import RankingService
from src.domain.services.scoring import ViralScoringService
from src.infrastructure.providers.export_provider import LocalExportProvider
from src.infrastructure.providers.gemini_provider import GeminiProvider
from src.infrastructure.providers.jikan_provider import JikanProvider
from src.infrastructure.providers.telegram_provider import TelegramProvider
from src.infrastructure.providers.tmdb_provider import TMDbProvider
from src.infrastructure.repositories.json_repo import (
    JsonBlacklistRepository,
    JsonHistoryRepository,
)


class Container:
    """
    Manual Dependency Injection container.
    Responsible for initializing and wiring application dependencies.
    """

    def __init__(self) -> None:
        self.settings: Settings = get_settings()

        # Shared HTTP Client for connection pooling with tuned performance limits
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self.http_client = httpx.AsyncClient(limits=limits)

        # Cache Provider
        from src.infrastructure.providers.cache_provider import InMemoryCacheProvider

        self.cache_provider = InMemoryCacheProvider()

        # Setup OpenTelemetry Metrics with Prometheus Exporter
        resource = Resource.create({"service.name": "cineops-ai"})
        self.metric_reader = PrometheusMetricReader()
        self.meter_provider = MeterProvider(
            resource=resource, metric_readers=[self.metric_reader]
        )
        metrics.set_meter_provider(self.meter_provider)
        self.meter = metrics.get_meter("cineops.telemetry")

        # Circuit Breakers
        self.tmdb_cb = CircuitBreaker(
            "tmdb", failure_threshold=5, recovery_timeout_sec=30.0
        )
        self.jikan_cb = CircuitBreaker(
            "jikan", failure_threshold=5, recovery_timeout_sec=30.0
        )
        self.gemini_cb = CircuitBreaker(
            "gemini", failure_threshold=3, recovery_timeout_sec=60.0
        )
        self.telegram_cb = CircuitBreaker(
            "telegram", failure_threshold=5, recovery_timeout_sec=30.0
        )

        # Initialize providers (injecting circuit breakers and cache)
        self.tmdb_provider = TMDbProvider(
            api_key=self.settings.tmdb_api_key,
            client=self.http_client,
            circuit_breaker=self.tmdb_cb,
            cache_provider=self.cache_provider,
            cache_ttl_seconds=self.settings.cache_ttl_seconds,
        )
        self.jikan_provider = JikanProvider(
            base_url=self.settings.jikan_base_url,
            client=self.http_client,
            circuit_breaker=self.jikan_cb,
            cache_provider=self.cache_provider,
            cache_ttl_seconds=self.settings.cache_ttl_seconds,
        )
        self.gemini_provider = GeminiProvider(
            api_key=self.settings.gemini_api_key,
            client=self.http_client,
            circuit_breaker=self.gemini_cb,
        )
        self.telegram_provider = TelegramProvider(
            bot_token=self.settings.telegram_bot_token,
            chat_id=self.settings.telegram_chat_id,
            client=self.http_client,
            circuit_breaker=self.telegram_cb,
        )

        # Repositories (JSON-backed for persistence)
        self.history_repo = JsonHistoryRepository(file_path=self.settings.storage_path)
        self.blacklist_repo = JsonBlacklistRepository(
            file_path=self.settings.cache_path
        )

        # Domain Services
        self.filter_service = MediaFilterService(min_rating=6.0)
        self.deduplication_service = DeduplicationService(
            self.history_repo, self.blacklist_repo
        )
        self.ranking_service = RankingService()
        self.scoring_service = ViralScoringService()

        # Application Services
        self.trending_service = TrendingService(
            providers=[self.tmdb_provider, self.jikan_provider]
        )
        self.prompt_builder = PromptBuilder()

        # Database session factory
        from src.infrastructure.database.database import AsyncSessionLocal

        self.db_session_factory = AsyncSessionLocal

        # Data Access Repositories
        from src.infrastructure.repositories.sqlalchemy_recommendation_repository import (
            SQLAlchemyRecommendationRepository,
        )

        self.db_recommendation_repo = SQLAlchemyRecommendationRepository(
            self.db_session_factory
        )

        from src.infrastructure.repositories.sqlalchemy_user_repository import (
            SQLAlchemyUserRepository,
        )

        self.user_repo = SQLAlchemyUserRepository(self.db_session_factory)

        from redis.asyncio import Redis

        from src.infrastructure.providers.redis_cache_provider import RedisCacheProvider

        self.redis_client = Redis.from_url(self.settings.redis_url)
        self.redis_cache_provider = RedisCacheProvider(self.redis_client)

        self.recommendation_service = RecommendationService(
            self.gemini_provider,
            self.prompt_builder,
            repository=self.db_recommendation_repo,
            cache=self.redis_cache_provider,
        )

        from src.application.services.auth import AuthService

        self.auth_service = AuthService(repository=self.user_repo)

        self.caption_service = CaptionGenerationService(self.gemini_provider)
        self.hashtag_service = HashtagGenerationService(self.gemini_provider)
        self.export_provider = LocalExportProvider(output_dir="output")

        self.workflow_coordinator = WorkflowCoordinator(
            trending_service=self.trending_service,
            deduplication_service=self.deduplication_service,
            filter_service=self.filter_service,
            ranking_service=self.ranking_service,
            recommendation_service=self.recommendation_service,
            scoring_service=self.scoring_service,
            export_provider=self.export_provider,
            history_repo=self.history_repo,
            notification_provider=self.telegram_provider,
        )

    @property
    def coordinator(self) -> WorkflowCoordinator:
        return self.workflow_coordinator

    async def close(self) -> None:
        """
        Cleanly shuts down all resources and connections within the container.
        """
        await self.http_client.aclose()
        if hasattr(self, "redis_cache_provider"):
            await self.redis_cache_provider.close()
