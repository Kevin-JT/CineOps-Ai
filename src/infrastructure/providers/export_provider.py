import json
import logging
from pathlib import Path

from src.domain.interfaces import ExportProvider
from src.domain.models.recommendation import Recommendation

logger = logging.getLogger(__name__)


class LocalExportProvider(ExportProvider):
    """
    Infrastructure provider responsible for exporting recommendations to local disk.
    """

    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = Path(output_dir)

    async def export_recommendation(self, recommendation: Recommendation) -> None:
        """
        Exports the recommendation as JSON and Markdown files.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        json_path = self.output_dir / "recommendation.json"
        md_path = self.output_dir / "recommendation.md"

        # Write JSON
        data = recommendation.model_dump(mode="json")
        try:
            json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            logger.info(f"Successfully exported recommendation JSON to {json_path}")
        except OSError as e:
            logger.error(f"Failed to write JSON export: {e}")
            raise

        # Write Markdown
        md_content = (
            f"# CineOps AI Recommendation\n\n"
            f"**ID**: {recommendation.id}\n"
            f"**Target Audience**: {recommendation.target_audience}\n"
            f"**Viral Score**: {recommendation.viral_score}/100\n\n"
            f"## Reasoning & Content\n\n"
            f"{recommendation.reasoning}\n\n"
        )

        if recommendation.content_strategy:
            st = recommendation.content_strategy
            md_content += (
                f"## Short-Form Content Strategy\n\n"
                f"**Video Hook**: {st.video_hook}\n\n"
                f"**On-Screen Text**:\n"
                f"- Opening: {st.on_screen_text.opening}\n"
                f"- Middle: {st.on_screen_text.middle}\n"
                f"- Ending: {st.on_screen_text.ending}\n\n"
                f"**Editing Instructions**: {st.editing_instructions}\n\n"
                f"**Caption**: {st.caption}\n\n"
                f"**Hashtags**: {' '.join(st.hashtags)}\n\n"
                f"**First Comment**: {st.first_comment}\n\n"
            )

        if recommendation.youtube_source:
            yt = recommendation.youtube_source
            md_content += (
                f"## YouTube Source Candidate\n\n"
                f"- **Title**: {yt.title}\n"
                f"- **Channel**: {yt.channel_name}\n"
                f"- **URL**: [{yt.url}]({yt.url})\n"
                f"- **Relevance Score**: {yt.relevance_score}/100\n"
                f"- **Timestamp**: Not verified\n\n"
            )

        md_content += "## Selected Item\n\n"

        for item in recommendation.items:
            md_content += (
                f"- **{item.title}** ({item.media_type})\n"
                f"  - Rating: {item.rating}\n"
                f"  - Overview: {item.overview}\n"
            )

        try:
            md_path.write_text(md_content, encoding="utf-8")
            logger.info(f"Successfully exported recommendation Markdown to {md_path}")
        except OSError as e:
            logger.error(f"Failed to write Markdown export: {e}")
            raise
