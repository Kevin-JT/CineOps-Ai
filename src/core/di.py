from src.application.services.coordinator import WorkflowCoordinator
from src.application.services.recommendation import RecommendationService
from src.application.services.trending import TrendingService
from src.config.settings import Settings, get_settings
from src.domain.services.deduplication import DeduplicationService
from src.domain.services.filtering import MediaFilterService
from src.domain.services.ranking import RankingService
from src.domain.services.scoring import ViralScoringService
from src.infrastructure.providers.export_provider import LocalExportProvider
from src.infrastructure.providers.gemini_provider import GeminiProvider
from src.infrastructure.providers.jikan_provider import JikanProvider
from src.infrastructure.providers.telegram_provider import TelegramProvider
from src.infrastructure.providers.tmdb_provider import TMDbProvider
from src.infrastructure.repositories.in_memory import (
    InMemoryBlacklistRepository,
    InMemoryHistoryRepository,
)


class Container:
    """
    Manual Dependency Injection container.
    Responsible for initializing and wiring application dependencies.
    """

    def __init__(self) -> None:
        self.settings: Settings = get_settings()

        # Initialize providers
        self.tmdb_provider = TMDbProvider(api_key=self.settings.tmdb_api_key)
        self.jikan_provider = JikanProvider(base_url=self.settings.jikan_base_url)
        self.gemini_provider = GeminiProvider(api_key=self.settings.gemini_api_key)
        self.telegram_provider = TelegramProvider(
            bot_token=self.settings.telegram_bot_token,
            chat_id=self.settings.telegram_chat_id,
        )

        # Repositories
        self.history_repo = InMemoryHistoryRepository()
        self.blacklist_repo = InMemoryBlacklistRepository()

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
        self.recommendation_service = RecommendationService(self.gemini_provider)
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
