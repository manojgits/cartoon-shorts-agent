"""
Cartoon Shorts Agent — Main Orchestrator

Finds trending cartoon YouTube Shorts and posts them to your Telegram channel.
Run with: python main.py [--dry-run]
"""

import argparse
import logging
import random
import sys

import config
from agent.youtube_fetcher import fetch_trending_cartoons
from agent.ranker import get_top_videos
from agent.dedup import load_posted_ids, add_posted_ids
from agent.telegram_poster import post_to_telegram

# ─── Logging Setup ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("agent")


def run(dry_run: bool = False):
    """Main agent execution flow."""

    # ── Step 1: Validate config ──────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("🤖 Cartoon Agent — Starting run")
    logger.info("=" * 60)

    try:
        config.validate_config()
    except EnvironmentError as e:
        logger.error(f"Config error: {e}")
        sys.exit(1)

    # ── Step 2: Pick a random subset of queries for variety ──────────────────
    num_queries = min(4, len(config.SEARCH_QUERIES))
    queries = random.sample(config.SEARCH_QUERIES, num_queries)
    logger.info(f"📝 Using {num_queries} search queries: {queries}")

    # ── Step 3: Fetch trending cartoons from YouTube ─────────────────────────
    logger.info("🔍 Searching YouTube for trending cartoons...")
    videos = fetch_trending_cartoons(
        api_key=config.YOUTUBE_API_KEY,
        queries=queries,
        max_age_hours=config.MAX_VIDEO_AGE_HOURS,
    )

    if not videos:
        logger.warning("⚠️  No videos found. Try adjusting search queries or age window.")
        return

    logger.info(f"📊 Found {len(videos)} cartoon videos total")

    # ── Step 4: Load dedup tracker and rank videos ───────────────────────────
    posted_ids = load_posted_ids(config.POSTED_VIDEOS_FILE)
    top_videos = get_top_videos(
        videos,
        posted_ids=posted_ids,
        max_count=config.MAX_POSTS_PER_RUN,
        max_age_hours=config.MAX_VIDEO_AGE_HOURS,
    )

    if not top_videos:
        logger.info("✅ All found videos have already been posted. Nothing new to share.")
        return

    # ── Step 5: Display results ──────────────────────────────────────────────
    logger.info(f"\n🏆 Top {len(top_videos)} videos to post:")
    for i, v in enumerate(top_videos, 1):
        logger.info(
            f"  {i}. [{v['score']:.3f}] {v['title'][:60]} "
            f"(👁 {v['views']:,} | ❤️ {v['likes']:,})"
        )

    # ── Step 6: Post to Telegram (or dry-run) ────────────────────────────────
    if dry_run:
        logger.info("🏃 DRY RUN — skipping Telegram posting.")
        logger.info("Run without --dry-run to actually post to your channel.")
    else:
        logger.info("📤 Posting to Telegram...")
        post_to_telegram(
            bot_token=config.TELEGRAM_BOT_TOKEN,
            chat_id=config.TELEGRAM_CHANNEL_ID,
            videos=top_videos,
        )

        # ── Step 7: Update dedup tracker ─────────────────────────────────────
        new_ids = [v["video_id"] for v in top_videos]
        add_posted_ids(config.POSTED_VIDEOS_FILE, new_ids)

    # ── Done ─────────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info(f"✅ Run complete! Posted {len(top_videos)} videos.")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cartoon Shorts Agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and rank videos without posting to Telegram",
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run)
