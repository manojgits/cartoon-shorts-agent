"""
Cartoon Agent — Main Orchestrator

Finds trending cartoon YouTube Shorts + full-length videos,
generates AI thumbnails & SEO, downloads them, uploads to YouTube
and Google Drive, and notifies you on Telegram.
Run with: python main.py [--dry-run]
"""

import argparse
import logging
import random
import sys

import config
from agent.youtube_fetcher import fetch_shorts, fetch_full_length
from agent.ranker import get_top_videos
from agent.dedup import load_posted_ids, add_posted_ids
from agent.downloader import download_videos
from agent.gemini_seo import generate_seo
from agent.thumbnail_maker import generate_thumbnail
from agent.youtube_uploader import upload_videos_to_youtube
from agent.drive_uploader import upload_videos, cleanup_downloads
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

    # ── Step 2: Load dedup tracker ───────────────────────────────────────────
    posted_ids = load_posted_ids(config.POSTED_VIDEOS_FILE)

    # ── Step 3: Fetch & rank SHORTS (pick top 1 by highest likes) ────────────
    logger.info("⚡ Fetching trending cartoon Shorts (≤60s)...")
    shorts_queries = random.sample(config.SHORTS_QUERIES, min(3, len(config.SHORTS_QUERIES)))
    shorts = fetch_shorts(config.YOUTUBE_API_KEY, shorts_queries, config.MAX_VIDEO_AGE_HOURS)
    top_shorts = get_top_videos(shorts, posted_ids, max_count=config.NUM_SHORTS, max_age_hours=config.MAX_VIDEO_AGE_HOURS)
    logger.info(f"📊 Selected {len(top_shorts)} Short(s)")

    # ── Step 4: Fetch & rank FULL-LENGTH (pick top 1 by highest likes) ───────
    logger.info("🎥 Fetching trending full-length cartoons (>60s)...")
    full_queries = random.sample(config.FULL_LENGTH_QUERIES, min(3, len(config.FULL_LENGTH_QUERIES)))
    full_videos = fetch_full_length(config.YOUTUBE_API_KEY, full_queries, config.MAX_VIDEO_AGE_HOURS)
    top_full = get_top_videos(full_videos, posted_ids, max_count=config.NUM_FULL_LENGTH, max_age_hours=config.MAX_VIDEO_AGE_HOURS)
    logger.info(f"📊 Selected {len(top_full)} full-length video(s)")

    # ── Step 5: Combine all videos ───────────────────────────────────────────
    all_videos = top_shorts + top_full
    if not all_videos:
        logger.warning("⚠️  No new videos found. Try adjusting queries or age window.")
        return

    logger.info(f"\n🏆 Top {len(all_videos)} videos to post:")
    for i, v in enumerate(all_videos, 1):
        vtype = "Short" if v["duration_seconds"] <= 60 else "Full"
        logger.info(
            f"  {i}. [{vtype}] [{v['score']:.3f}] {v['title'][:50]} "
            f"(👁 {v['views']:,} | ❤️ {v['likes']:,})"
        )

    if dry_run:
        logger.info("🏃 DRY RUN — skipping download, upload, and Telegram posting.")
        return

    # ── Step 6: Download videos ──────────────────────────────────────────────
    logger.info("⬇️ Downloading videos...")
    all_videos = download_videos(all_videos, config.DOWNLOADS_DIR)

    # ── Step 7: Filter to only successfully downloaded videos ────────────────
    downloaded = [v for v in all_videos if v.get("file_path")]
    skipped = len(all_videos) - len(downloaded)
    if skipped:
        logger.warning(f"⚠️ {skipped} video(s) failed to download, skipping them.")
    if not downloaded:
        logger.error("❌ No videos were downloaded. Aborting run.")
        return
    logger.info(f"✅ {len(downloaded)} video(s) ready for upload.")

    # From here on, only work with successfully downloaded videos
    all_videos = downloaded

    # ── Step 8: Generate SEO with Gemini ─────────────────────────────────────
    if config.GEMINI_API_KEY:
        logger.info("✨ Generating SEO with Gemini AI...")
        for video in all_videos:
            vtype = "Short" if video.get("duration_seconds", 0) <= 60 else "Full"
            seo = generate_seo(config.GEMINI_API_KEY, video["title"], vtype)
            if seo:
                video["seo_title"] = seo["title"]
                video["seo_description"] = seo["description"]
                video["seo_tags"] = seo["tags"]
            else:
                video["seo_title"] = video["title"]
                video["seo_description"] = ""
                video["seo_tags"] = []
    else:
        logger.info("⏭️ Skipping SEO generation (no GEMINI_API_KEY)")
        for video in all_videos:
            video["seo_title"] = video["title"]
            video["seo_description"] = ""
            video["seo_tags"] = []

    # ── Step 9: Generate thumbnails with Nano Banana ─────────────────────────
    if config.GEMINI_API_KEY:
        logger.info("🎨 Generating AI thumbnails with Nano Banana...")
        for video in all_videos:
            thumb = generate_thumbnail(
                api_key=config.GEMINI_API_KEY,
                title=video["title"],
                seo_title=video.get("seo_title", video["title"]),
                output_dir=config.DOWNLOADS_DIR,
                video_id=video["video_id"],
            )
            video["thumbnail_path"] = thumb
    else:
        logger.info("⏭️ Skipping thumbnail generation (no GEMINI_API_KEY)")

    # ── Step 10: Upload to YouTube ───────────────────────────────────────────
    logger.info("🎬 Uploading to YouTube channel...")
    all_videos = upload_videos_to_youtube(
        token_file=config.TOKEN_FILE,
        videos=all_videos,
        privacy=config.YOUTUBE_PRIVACY,
    )

    # ── Step 11: Upload to Google Drive ──────────────────────────────────────
    logger.info("☁️ Uploading to Google Drive...")
    all_videos = upload_videos(
        token_file=config.TOKEN_FILE,
        folder_id=config.GOOGLE_DRIVE_FOLDER_ID,
        videos=all_videos,
    )

    # ── Step 12: Post to Telegram ────────────────────────────────────────────
    logger.info("📤 Sending to Telegram...")
    post_to_telegram(
        bot_token=config.TELEGRAM_BOT_TOKEN,
        chat_id=config.TELEGRAM_CHANNEL_ID,
        videos=all_videos,
    )

    # ── Step 13: Update dedup tracker ────────────────────────────────────────
    # Only mark successfully processed videos as posted
    new_ids = [v["video_id"] for v in all_videos]
    add_posted_ids(config.POSTED_VIDEOS_FILE, new_ids)

    # ── Step 14: Cleanup downloads ───────────────────────────────────────────
    cleanup_downloads(config.DOWNLOADS_DIR)

    # ── Done ─────────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info(f"✅ Run complete! Processed {len(all_videos)} videos.")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cartoon Agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and rank videos without downloading/posting",
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run)
