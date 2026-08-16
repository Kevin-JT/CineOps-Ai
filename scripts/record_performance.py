import argparse
import asyncio
import sys

from src.core.di import Container
from src.domain.models.performance import PerformanceMetrics


async def record_performance(args: argparse.Namespace) -> None:
    container = Container()
    try:
        metrics = PerformanceMetrics(
            recommendation_id=args.recommendation_id,
            platform=args.platform,
            views=args.views,
            likes=args.likes,
            comments=args.comments,
            shares=args.shares,
            saves=args.saves,
            retention_rate=args.retention,
        )

        success = await container.history_repo.save_performance(metrics)
        if success:
            print(f"✅ Performance metrics recorded for '{metrics.recommendation_id}':")
            print(f"   Platform: {metrics.platform}")
            print(f"   Views: {metrics.views:,}")
            if metrics.likes is not None:
                print(f"   Likes: {metrics.likes:,}")
            if metrics.comments is not None:
                print(f"   Comments: {metrics.comments:,}")
            if metrics.shares is not None:
                print(f"   Shares: {metrics.shares:,}")
            if metrics.saves is not None:
                print(f"   Saves: {metrics.saves:,}")
            if metrics.engagement_rate is not None:
                print(f"   Engagement Rate: {metrics.engagement_rate:.2f}%")
        else:
            print("❌ Failed to record performance metrics.", file=sys.stderr)
            sys.exit(1)
    finally:
        await container.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Record performance metrics for CineOps recommendations."
    )
    parser.add_argument(
        "--recommendation-id", required=True, help="Recommendation ID or Item ID"
    )
    parser.add_argument(
        "--platform",
        required=True,
        choices=["instagram", "youtube", "tiktok", "twitter", "other"],
        help="Social media platform",
    )
    parser.add_argument("--views", required=True, type=int, help="Total view count")
    parser.add_argument("--likes", type=int, default=None, help="Total likes count")
    parser.add_argument(
        "--comments", type=int, default=None, help="Total comments count"
    )
    parser.add_argument("--shares", type=int, default=None, help="Total shares count")
    parser.add_argument("--saves", type=int, default=None, help="Total saves count")
    parser.add_argument(
        "--retention",
        type=float,
        default=None,
        help="Retention rate percentage (0-100)",
    )

    args = parser.parse_args()

    if args.views < 0:
        print("Error: --views cannot be negative.", file=sys.stderr)
        sys.exit(1)

    asyncio.run(record_performance(args))


if __name__ == "__main__":
    main()
