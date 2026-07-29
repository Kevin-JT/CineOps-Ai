"""
Dependency Injection Container for manual wiring of services.
"""

from src.config.settings import Settings, get_settings


class Container:
    """
    Manual Dependency Injection container.
    Responsible for initializing and wiring application dependencies.
    """

    def __init__(self) -> None:
        self.settings: Settings = get_settings()

        # In the future, we will initialize providers here
        # self.tmdb_provider = TMDbProvider(api_key=self.settings.tmdb_api_key)
        # self.jikan_provider = JikanProvider(base_url=self.settings.jikan_base_url)
        # self.gemini_provider = GeminiProvider(api_key=self.settings.gemini_api_key)
        # self.telegram_provider = TelegramProvider(token=self.settings.telegram_bot_token)

        # Repositories
        # self.history_repo = HistoryRepository(self.settings.storage_path)

        # Services
        # self.recommendation_service = RecommendationService(
        #     self.tmdb_provider, self.jikan_provider, self.gemini_provider, self.history_repo
        # )

    # Example property to retrieve a fully constructed service
    # @property
    # def recommendation_pipeline(self) -> RecommendationService:
    #     return self.recommendation_service
