from src.domain.models.ai_response import AIRecommendationResponse
from src.domain.models.media_item import MediaItem


class PromptBuilder:
    """
    Constructs highly specific prompts for the AI provider, enforcing structured JSON output.
    """

    SYSTEM_PROMPT = (
        "You are an expert content curator for a highly engaging social media account called CineOps.\n"
        "Your task is to review trending media items and select exactly ONE item that has the highest potential "
        "to go viral with our audience.\n\n"
        "CRITICAL RULES:\n"
        "1. You MUST respond ONLY with a valid JSON object matching the exact schema provided.\n"
        "2. Do NOT wrap the JSON in Markdown block ticks (e.g. ```json). Output raw JSON.\n"
        "3. Provide a confidence_score between 0.0 and 100.0 indicating how strongly you believe this will go viral.\n"
        "4. The selected_id MUST precisely match one of the items in the list.\n"
    )

    def build_recommendation_prompt(self, items: list[MediaItem]) -> str:
        """
        Builds a comprehensive prompt with context and schema definition.
        """
        context_str = self._format_items_context(items)
        schema_str = self._get_json_schema()

        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"--- TRENDING MEDIA ITEMS ---\n"
            f"{context_str}\n\n"
            f"--- EXPECTED JSON SCHEMA ---\n"
            f"{schema_str}\n"
        )

    def _format_items_context(self, items: list[MediaItem]) -> str:
        """
        Formats the media items into a readable context block.
        """
        items_context = []
        for i, item in enumerate(items, 1):
            items_context.append(
                f"Item {i}:\n"
                f"- ID: {item.id}\n"
                f"- Title: {item.title} ({item.media_type})\n"
                f"- Rating: {item.rating}/10\n"
                f"- Popularity: {item.popularity}\n"
                f"- Overview: {item.overview}\n"
            )
        return "\n".join(items_context)

    def _get_json_schema(self) -> str:
        """
        Extracts the JSON schema directly from the Pydantic model definition.
        """
        schema = AIRecommendationResponse.model_json_schema()

        # We can format it as a string representation of the dict for the prompt
        import json

        return json.dumps(schema, indent=2)
