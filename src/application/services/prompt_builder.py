from src.domain.models.ai_response import AIRecommendationResponse
from src.domain.models.media_item import MediaItem


class PromptBuilder:
    """
    Constructs highly specific prompts for the AI provider, enforcing structured JSON output.
    """

    SYSTEM_PROMPT = (
        "You are an expert cinematic short-form content strategist for a social media account called CineOps.\n"
        "Your task is to review trending media items and select exactly ONE item that has the highest potential "
        "to go viral as a Reel or Short, providing a complete short-form content strategy.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Analyze candidate media items and select the strongest content opportunity.\n"
        "2. Explain why the opportunity works in 'reasoning_why_now' and 'reasoning_audience_appeal'.\n"
        "3. Generate a 'video_hook': a short, strong opening hook for the first seconds of the video.\n"
        "4. Generate 'on_screen_text': structured text overlays with 'opening', 'middle', and 'ending' fields.\n"
        "5. Generate 'editing_instructions': practical editing guidance (pacing, visual impact moments, text placement, ending style).\n"
        "6. DO NOT INVENT TIMESTAMPS: Never invent or fabricate exact scene timestamps in editing instructions.\n"
        "7. Generate a 'caption': an authentic, engaging social media caption (avoid generic AI tropes or keyword stuffing).\n"
        "8. Generate 'hashtags': exactly 5 highly relevant hashtags as a list of 5 strings.\n"
        "9. Generate a 'first_comment': a natural discussion-provoking comment or question without engagement bait.\n"
        "10. Keep all recommendations grounded in the provided media information.\n"
        "11. You MUST respond ONLY with a valid JSON object matching the exact schema provided.\n"
        "12. Do NOT wrap the JSON in Markdown block ticks (e.g. ```json). Output raw JSON.\n"
        "13. Provide a confidence_score between 0.0 and 100.0.\n"
        "14. The selected_id MUST precisely match one of the items in the list.\n"
    )

    def build_recommendation_prompt(
        self,
        items: list[MediaItem],
        performance_summary: str | None = None,
        strategy_context: str | None = None,
    ) -> str:
        """
        Builds a comprehensive prompt with context, optional historical performance insights, strategic objective, and schema definition.
        """
        context_str = self._format_items_context(items)
        schema_str = self._get_json_schema()

        prompt_parts = [
            self.SYSTEM_PROMPT,
            "--- TRENDING MEDIA ITEMS ---",
            context_str,
        ]

        if strategy_context:
            prompt_parts.extend(
                [
                    "--- TODAY'S STRATEGIC GROWTH OBJECTIVE ---",
                    strategy_context,
                    (
                        "INSTRUCTION: Align the short-form video hook, caption, and editing plan "
                        "with today's strategic growth objective where appropriate, without forcing a poor fit."
                    ),
                ]
            )

        if performance_summary:
            prompt_parts.extend(
                [
                    "--- HISTORICAL PERFORMANCE INSIGHTS ---",
                    performance_summary,
                    (
                        "INSTRUCTION: Use these historical performance insights as supporting evidence "
                        "when creating the recommendation content strategy. Do not treat them as rigid rules."
                    ),
                ]
            )

        prompt_parts.extend(
            [
                "--- EXPECTED JSON SCHEMA ---",
                schema_str,
            ]
        )

        return "\n\n".join(prompt_parts)

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
