import logging

from pydantic import ValidationError

from src.application.services.prompt_builder import PromptBuilder
from src.core.exceptions import CineOpsError
from src.domain.interfaces import AIProvider
from src.domain.models.ai_response import AIRecommendationResponse
from src.domain.models.media_item import MediaItem
from src.domain.models.recommendation import Recommendation

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service responsible for orchestrating the AI to generate a recommendation.
    """

    def __init__(self, ai_provider: AIProvider, prompt_builder: PromptBuilder) -> None:
        self.ai_provider = ai_provider
        self.prompt_builder = prompt_builder

    async def generate_recommendation(self, items: list[MediaItem]) -> Recommendation:
        """
        Constructs a prompt based on the provided media items and requests an AI recommendation.

        Args:
            items: The top ranked items to choose from.

        Returns:
            A Recommendation object.

        Raises:
            CineOpsError: If the AI response is invalid or missing.
        """
        if not items:
            raise ValueError("Cannot generate recommendation without media items.")

        prompt = self.prompt_builder.build_recommendation_prompt(items)
        logger.info("Sending prompt to AI provider...")

        response_text = await self.ai_provider.generate_recommendations(prompt)

        return self._parse_response(response_text, items)

    def _parse_response(
        self, response_text: str, items: list[MediaItem]
    ) -> Recommendation:
        """
        Parses the AI's JSON response and constructs a Recommendation model.
        """
        # Clean potential markdown wrapping
        cleaned_text = response_text.strip()
        cleaned_text = cleaned_text.removeprefix("```json")
        cleaned_text = cleaned_text.removeprefix("```")
        cleaned_text = cleaned_text.removesuffix("```")

        try:
            parsed_data = AIRecommendationResponse.model_validate_json(
                cleaned_text.strip()
            )
        except ValidationError as e:
            logger.error(f"Failed to parse AI JSON response: {cleaned_text}")
            logger.error(f"Validation error: {e}")
            raise CineOpsError("AI provided invalid JSON format.") from e
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            raise CineOpsError("Unexpected error parsing AI response.") from e

        selected_id = parsed_data.selected_id

        # Format a richer reasoning block explaining "why now" and "audience appeal"
        full_reasoning = (
            f"**Why Now**: {parsed_data.reasoning_why_now}\n\n"
            f"**Audience Appeal**: {parsed_data.reasoning_audience_appeal}\n\n"
            f"**Caption**: {parsed_data.caption}\n"
            f"**Hashtags**: {' '.join(parsed_data.hashtags)}"
        )

        selected_item = next((i for i in items if i.id == selected_id), None)
        if not selected_item:
            logger.error(f"AI selected invalid ID '{selected_id}'.")
            raise CineOpsError(f"AI hallucinated an invalid media ID: {selected_id}")

        logger.info(
            f"AI successfully recommended item '{selected_item.title}' "
            f"with confidence score {parsed_data.confidence_score}."
        )

        return Recommendation(
            id=f"rec_{selected_item.id}",
            items=[selected_item],
            target_audience=parsed_data.target_audience,
            reasoning=full_reasoning,
            confidence_score=parsed_data.confidence_score,
        )
