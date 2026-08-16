import asyncio
import logging

from src.application.services.recommendation import RecommendationService
from src.application.services.trending import TrendingService
from src.config.settings import Settings, get_settings
from src.core.exceptions import CineOpsError
from src.domain.interfaces import (
    ExportProvider,
    HistoryRepository,
    NotificationProvider,
    SourceProvider,
)
from src.domain.models.candidate import EvaluatedCandidate
from src.domain.models.media_item import MediaItem
from src.domain.models.quality import (
    OpportunityCategory,
    OpportunityScore,
    OpportunityScoreBreakdown,
)
from src.domain.models.scoring import ViralScoreFactors
from src.domain.services.deduplication import DeduplicationService
from src.domain.services.filtering import MediaFilterService
from src.domain.services.performance_analyzer import (
    PerformanceAnalyzer,
    PerformanceInsightResult,
)
from src.domain.services.quality_engine import RecommendationQualityEngine
from src.domain.services.ranking import RankingService
from src.domain.services.scoring import ViralScoringService

logger = logging.getLogger(__name__)


class WorkflowCoordinator:
    """
    Orchestrates the entire recommendation lifecycle, coordinating Domain and Application services.
    Supports multi-candidate parallel evaluation, deterministic selection, and failure isolation.
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
        quality_engine: RecommendationQualityEngine | None = None,
        settings: Settings | None = None,
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
        self.quality_engine = quality_engine
        self.settings = settings or get_settings()

    async def _evaluate_single_candidate(
        self,
        candidate_item: MediaItem,
        performance_summary: str | None,
        insight_result: PerformanceInsightResult | None,
    ) -> EvaluatedCandidate | None:
        """
        Evaluates a single candidate item through AI recommendation, YouTube discovery, and Quality Engine scoring.
        Failures are trapped so one candidate failure does not break the entire pipeline.
        """
        try:
            # 1. AI Recommendation Generation
            rec = await self.recommendation_service.generate_recommendation(
                [candidate_item], performance_summary=performance_summary
            )

            # 2. Viral Score calculation
            factors = ViralScoreFactors(
                popularity=min(candidate_item.popularity, 100.0),
                rating=candidate_item.rating,
                recognition=80.0,
                visual_impact=85.0,
                emotional_impact=70.0,
                social_potential=90.0,
            )
            viral_result = self.scoring_service.calculate_score(factors)
            rec = rec.model_copy(update={"viral_score": viral_result.score})

            # 3. YouTube Source Discovery (isolated)
            if self.source_provider:
                try:
                    keywords = []
                    if rec.content_strategy:
                        keywords.append(rec.content_strategy.video_hook)
                    yt_source = await self.source_provider.search_source(
                        media_title=candidate_item.title,
                        media_type=candidate_item.media_type,
                        query_keywords=keywords,
                    )
                    if yt_source:
                        rec = rec.model_copy(update={"youtube_source": yt_source})
                except Exception as e:  # noqa: BLE001
                    logger.warning(
                        f"YouTube discovery failed for '{candidate_item.title}': {e}"
                    )

            # 4. Recommendation Quality Engine Evaluation (isolated)
            opp_score: OpportunityScore
            if self.quality_engine:
                opp_score = self.quality_engine.evaluate(
                    recommendation=rec,
                    selected_item=candidate_item,
                    youtube_source=rec.youtube_source,
                    performance_result=insight_result,
                )
            else:
                opp_score = OpportunityScore(
                    final_score=int(viral_result.score),
                    category=OpportunityCategory.STRONG,
                    breakdown=OpportunityScoreBreakdown(
                        content_score=viral_result.score,
                        short_form_score=viral_result.score,
                        source_score=50.0,
                        historical_score=50.0,
                    ),
                )

            rec = rec.model_copy(update={"opportunity_score": opp_score})
            return EvaluatedCandidate(
                item=candidate_item,
                recommendation=rec,
                opportunity_score=opp_score,
            )
        except Exception:
            logger.exception(
                f"Candidate '{candidate_item.title}' evaluation failed gracefully."
            )
            return None

    async def run_pipeline(self) -> None:
        """
        Executes the full pipeline:
        Fetch -> Deduplicate -> Filter -> Initial Rank -> Multi-Candidate Parallel Evaluation -> Deterministic Selection -> Save -> Export -> Notify.
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

            # 4. Rank & Select Candidate Pool
            ranked_items = self.ranking_service.rank_by_popularity(filtered_items)
            candidate_pool = ranked_items[: self.settings.candidate_count]

            # 4b. Performance Analysis (Optional learning loop)
            performance_summary = None
            learning_insight = None
            insight_result = None
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

            # 5. Multi-Candidate Parallel Evaluation
            logger.info(
                f"Evaluating top {len(candidate_pool)} candidates concurrently..."
            )
            eval_tasks = [
                self._evaluate_single_candidate(
                    candidate_item=item,
                    performance_summary=performance_summary,
                    insight_result=insight_result,
                )
                for item in candidate_pool
            ]
            raw_results = await asyncio.gather(*eval_tasks, return_exceptions=True)

            valid_candidates: list[EvaluatedCandidate] = [
                r for r in raw_results if isinstance(r, EvaluatedCandidate)
            ]

            if not valid_candidates:
                logger.warning("All candidate evaluations failed. Aborting pipeline.")
                return

            # 6. Deterministic Selection & Tie-Breaking
            valid_candidates.sort(
                key=lambda c: (
                    c.opportunity_score.final_score,
                    c.opportunity_score.breakdown.short_form_score,
                    c.opportunity_score.breakdown.source_score,
                    c.opportunity_score.breakdown.content_score,
                    c.item.popularity,
                ),
                reverse=True,
            )

            winner = valid_candidates[0]
            alternatives = valid_candidates[1:4]  # Top 3 alternatives

            selected_item = winner.item
            final_recommendation = winner.recommendation

            # Check Minimum Opportunity Score Threshold
            threshold_warning = ""
            if (
                winner.opportunity_score.final_score
                < self.settings.min_opportunity_score
            ):
                threshold_warning = (
                    f"⚠️ *NOTE*: Best candidate scored {winner.opportunity_score.final_score}/100 "
                    f"(below minimum target of {self.settings.min_opportunity_score}/100).\n\n"
                )
                logger.warning(
                    f"Winner '{selected_item.title}' scored {winner.opportunity_score.final_score}, "
                    f"which is below min_opportunity_score ({self.settings.min_opportunity_score})."
                )

            # 7. Save Winner to History
            await self.history_repo.save(selected_item)

            # 8. Export Winner
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

                opp = winner.opportunity_score
                bd = opp.breakdown
                strengths_str = (
                    "\n".join(f"• {s}" for s in opp.strengths)
                    if opp.strengths
                    else "• N/A"
                )
                weaknesses_str = (
                    "\n".join(f"• {w}" for w in opp.weaknesses)
                    if opp.weaknesses
                    else "• N/A"
                )

                quality_block = (
                    f"🎯 *OPPORTUNITY SCORE*: {opp.final_score}/100 ({opp.category.value})\n\n"
                    f"📊 *SCORE BREAKDOWN*\n"
                    f"Content Potential: {int(bd.content_score)}/100\n"
                    f"Short-form Potential: {int(bd.short_form_score)}/100\n"
                    f"Source Quality: {int(bd.source_score)}/100\n"
                    f"Historical Evidence: {int(bd.historical_score)}/100\n\n"
                    f"💪 *WHY THIS WON*\n"
                    f"{strengths_str}\n\n"
                    f"⚠️ *LIMITATIONS*\n"
                    f"{weaknesses_str}\n\n"
                )

                alt_lines = []
                for idx, alt in enumerate(alternatives, 2):
                    alt_lines.append(
                        f"{idx}. {alt.item.title} — {alt.opportunity_score.final_score}/100 ({alt.opportunity_score.category.value})"
                    )

                alt_block = (
                    "🥈 *TOP ALTERNATIVES*\n" + "\n".join(alt_lines) + "\n\n"
                    if alt_lines
                    else ""
                )

                message = (
                    f"🎬 *CINEOPS CONTENT OPPORTUNITY*\n\n"
                    f"*SELECTED FROM {len(valid_candidates)} CANDIDATES*\n\n"
                    f"🎥 *MOVIE / SERIES / ANIME*\n"
                    f"{selected_item.title} ({selected_item.media_type})\n\n"
                    f"{threshold_warning}"
                    f"{quality_block}"
                    f"{alt_block}"
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
