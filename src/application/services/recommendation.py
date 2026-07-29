import json
import logging
from typing import Any

from src.core.exceptions import CineOpsError
from src.domain.interfaces import AIProvider
from src.domain.models.media_item import MediaItem
from src.domain.models.recommendation import Recommendation

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service responsible for orchestrating the AI to generate a recommendation.
    """

    def __init__(self, ai_provider: AIProvider) -> None:
        self.ai_provider = ai_provider

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

        prompt = self._build_prompt(items)
        logger.info("Sending prompt to AI provider...")

        response_text = await self.ai_provider.generate_recommendations(prompt)

        return self._parse_response(response_text, items)

    def _build_prompt(self, items: list[MediaItem]) -> str:
        """
        Builds the prompt instructing the AI on what to generate.
        """
        items_context = []
        for i, item in enumerate(items, 1):
            items_context.append(
                f"{i}. Title: {item.title} ({item.media_type})\n"
                f"   Rating: {item.rating}\n"
                f"   Overview: {item.overview}\n"
            )

        context_str = "\n".join(items_context)

        return (
            "You are an expert content curator for a highly engaging social media account called CineOps.\n"
            "Review the following trending media items:\n\n"
            f"{context_str}\n\n"
            "Select exactly ONE item from the list above that would make the most viral and engaging post.\n"
            "Respond ONLY with a valid JSON object matching this exact structure:\n"
            "{\n"
            '  "selected_id": "the exact ID of the item you chose",\n'
            '  "target_audience": "description of the target audience",\n'
            '  "reasoning": "why this item is highly engaging right now",\n'
            '  "caption": "a highly engaging, viral-optimized social media caption",\n'
            '  "hashtags": ["#viral", "#trending"]\n'
            "}\n"
            "Do not include any Markdown formatting (like ```json), just the raw JSON object."
        )

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
            data: dict[str, Any] = json.loads(cleaned_text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {cleaned_text}")
            raise CineOpsError("AI provided invalid JSON format.") from e

        selected_id = str(data.get("selected_id", ""))
        target_audience = str(data.get("target_audience", "General"))
        reasoning = str(data.get("reasoning", "No reasoning provided."))

        # Combine the caption and hashtags into the reasoning/caption for now,
        # or we could add them to the Recommendation model if needed.
        # Since the model has target_audience and reasoning, we'll store them there.
        # Wait, the prompt generated "caption" and "hashtags". Let's append them to reasoning for storage,
        # or we could update the Recommendation model. For now, append to reasoning to keep the domain pure.
        caption = data.get("caption", "")
        hashtags = " ".join(data.get("hashtags", []))

        full_reasoning = f"{reasoning}\n\nCaption: {caption}\nHashtags: {hashtags}"

        selected_item = next((i for i in items if i.id == selected_id), None)
        if not selected_item:
            # Fallback to the first item if the AI hallucinates an ID
            logger.warning(
                f"AI selected invalid ID '{selected_id}'. Falling back to first item."
            )
            selected_item = items[0]

        logger.info(f"AI successfully recommended item '{selected_item.title}'.")

        return Recommendation(
            id=f"rec_{selected_item.id}",
            items=[selected_item],
            target_audience=target_audience,
            reasoning=full_reasoning,
        )
