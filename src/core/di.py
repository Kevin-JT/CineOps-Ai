from src.config.settings import Settings, get_settings
from src.infrastructure.providers.gemini_provider import GeminiProvider
from src.infrastructure.providers.jikan_provider import JikanProvider
from src.infrastructure.providers.telegram_provider import TelegramProvider
from src.infrastructure.providers.tmdb_provider import TMDbProvider


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
        # self.history_repo = HistoryRepository(self.settings.storage_path)

        # Services
        # self.recommendation_service = RecommendationService(
        #     self.tmdb_provider, self.jikan_provider, self.gemini_provider, self.history_repo
        # )

    # Example property to retrieve a fully constructed service
    # @property
    # def recommendation_pipeline(self) -> RecommendationService:
    #     return self.recommendation_service
