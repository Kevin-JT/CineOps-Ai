import logging

from src.application.services.recommendation import RecommendationService
from src.application.services.trending import TrendingService
from src.core.exceptions import CineOpsError
from src.domain.interfaces import (
    ExportProvider,
    HistoryRepository,
    NotificationProvider,
    SourceProvider,
)
from src.domain.models.scoring import ViralScoreFactors
from src.domain.services.deduplication import DeduplicationService
from src.domain.services.filtering import MediaFilterService
from src.domain.services.performance_analyzer import PerformanceAnalyzer
from src.domain.services.ranking import RankingService
from src.domain.services.scoring import ViralScoringService

logger = logging.getLogger(__name__)


class WorkflowCoordinator:
    """
    Orchestrates the entire recommendation lifecycle, coordinating Domain and Application services.
    """

    def __init__(
        self,
        trending_service: TrendingService,
        deduplication_service: DeduplicationService,
        filter_service: MediaFilterService,
        ranking_service: RankingService,
        recommendation_service: RecommendationService,
        scoring_service: ViralScoringService,
        export_provider: ExportProvider,
        history_repo: HistoryRepository,
        notification_provider: NotificationProvider,
        source_provider: SourceProvider | None = None,
        performance_analyzer: PerformanceAnalyzer | None = None,
    ) -> None:
        self.trending_service = trending_service
        self.deduplication_service = deduplication_service
        self.filter_service = filter_service
        self.ranking_service = ranking_service
        self.recommendation_service = recommendation_service
        self.scoring_service = scoring_service
        self.export_provider = export_provider
        self.history_repo = history_repo
        self.notification_provider = notification_provider
        self.source_provider = source_provider
        self.performance_analyzer = performance_analyzer

    async def run_pipeline(self) -> None:
        """
        Executes the full pipeline:
        Fetch -> Deduplicate -> Filter -> Rank -> Performance Analysis -> Recommend -> Score -> Discover Source -> Save -> Export -> Notify.
        """
        logger.info("Starting CineOps AI recommendation pipeline...")

        try:
            # 1. Fetch
            items = await self.trending_service.fetch_all_trending()
            if not items:
                logger.warning("No trending items fetched. Aborting pipeline.")
                return

            # 2. Deduplicate
            unique_items = await self.deduplication_service.filter_duplicates(items)
            if not unique_items:
                logger.warning(
                    "No unique items left after deduplication. Aborting pipeline."
                )
                return

            # 3. Filter
            filtered_items = self.filter_service.filter_items(unique_items)
            if not filtered_items:
                logger.warning(
                    "No items passed the quality filters. Aborting pipeline."
                )
                return

            # 4. Rank & Select Top N
            ranked_items = self.ranking_service.rank_by_popularity(filtered_items)
            top_items = ranked_items[:10]  # Pass top 10 to AI for context limit safety

            # 4b. Performance Analysis (Optional learning loop)
            performance_summary = None
            learning_insight = None
            if self.performance_analyzer:
                try:
                    perf_records = await self.history_repo.get_all_performance()
                    insight_result = self.performance_analyzer.analyze_performance(
                        perf_records
                    )
                    if insight_result.has_enough_data:
                        performance_summary = insight_result.formatted_summary
                        learning_insight = insight_result.short_insight
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Performance analysis failed gracefully: {e}")

            # 5. Generate Recommendation
            recommendation = await self.recommendation_service.generate_recommendation(
                top_items, performance_summary=performance_summary
            )

            # 6. Calculate Viral Score
            selected_item = recommendation.items[0]
            factors = ViralScoreFactors(
                popularity=min(
                    selected_item.popularity, 100.0
                ),  # Normalize for domain constraint
                rating=selected_item.rating,
                recognition=80.0,  # Assumed AI/Defaults for now
                visual_impact=85.0,
                emotional_impact=70.0,
                social_potential=90.0,
            )
            viral_score_result = self.scoring_service.calculate_score(factors)

            # Since Recommendation is immutable, we create a new instance with the viral score
            final_recommendation = recommendation.model_copy(
                update={"viral_score": viral_score_result.score}
            )

            # 6b. YouTube Source Discovery (Graceful optional enhancement)
            if self.source_provider:
                try:
                    keywords = []
                    if final_recommendation.content_strategy:
                        keywords.append(
                            final_recommendation.content_strategy.video_hook
                        )
                    yt_source = await self.source_provider.search_source(
                        media_title=selected_item.title,
                        media_type=selected_item.media_type,
                        query_keywords=keywords,
                    )
                    if yt_source:
                        final_recommendation = final_recommendation.model_copy(
                            update={"youtube_source": yt_source}
                        )
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"YouTube discovery failed gracefully: {e}")

            # 7. Save to History
            await self.history_repo.save(selected_item)

            # 8. Export
            await self.export_provider.export_recommendation(final_recommendation)

            # 9. Notify
            strategy = final_recommendation.content_strategy
            if strategy:
                if final_recommendation.youtube_source:
                    yt = final_recommendation.youtube_source
                    source_block = (
                        f"🎥 *YOUTUBE SOURCE*\n"
                        f"Title: {yt.title}\n"
                        f"Channel: {yt.channel_name}\n"
                        f"Relevance: {int(yt.relevance_score)}/100\n\n"
                        f"⏱ *TIMESTAMP*\n"
                        f"Timestamp: Not verified\n\n"
                        f"▶️ *SOURCE*\n"
                        f"{yt.url}"
                    )
                else:
                    source_block = (
                        "⚠️ *SOURCE / CLIP*\n"
                        "Not available — YouTube discovery skipped or no match found."
                    )

                insight_block = (
                    f"💡 *LEARNING INSIGHT*\n{learning_insight}\n\n"
                    if learning_insight
                    else ""
                )

                message = (
                    f"🎬 *CINEOPS CONTENT OPPORTUNITY*\n\n"
                    f"🎥 *MOVIE / SERIES / ANIME*\n"
                    f"{selected_item.title} ({selected_item.media_type})\n\n"
                    f"🔥 *VIRAL OPPORTUNITY*\n"
                    f"{int(viral_score_result.score)}/100\n\n"
                    f"🎯 *TARGET AUDIENCE*\n"
                    f"{final_recommendation.target_audience}\n\n"
                    f"🪝 *HOOK*\n"
                    f'"{strategy.video_hook}"\n\n'
                    f"📝 *ON-SCREEN TEXT*\n"
                    f"Opening: {strategy.on_screen_text.opening}\n"
                    f"Middle: {strategy.on_screen_text.middle}\n"
                    f"Ending: {strategy.on_screen_text.ending}\n\n"
                    f"✂️ *EDITING PLAN*\n"
                    f"{strategy.editing_instructions}\n\n"
                    f"📝 *CAPTION*\n"
                    f"{strategy.caption}\n\n"
                    f"#️⃣ *HASHTAGS*\n"
                    f"{' '.join(strategy.hashtags)}\n\n"
                    f"💬 *FIRST COMMENT*\n"
                    f"{strategy.first_comment}\n\n"
                    f"🧠 *WHY THIS WORKS*\n"
                    f"{final_recommendation.reasoning}\n\n"
                    f"{insight_block}"
                    f"{source_block}"
                )
            else:
                message = (
                    f"🎬 *New Recommendation Ready!*\n\n"
                    f"**{selected_item.title}** ({selected_item.media_type})\n"
                    f"Viral Score: {viral_score_result.score}/100\n"
                    f"AI Confidence: {final_recommendation.confidence_score}/100\n\n"
                    f"Check the output directory for details!"
                )
            await self.notification_provider.send_message(message)

            logger.info("Pipeline completed successfully!")

        except Exception as e:
            logger.critical(
                f"Pipeline failed with an unexpected error: {e}", exc_info=True
            )
            raise CineOpsError(f"Pipeline execution failed: {e}") from e
