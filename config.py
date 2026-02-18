"""
Configuration module — loads all settings from environment variables.
"""

import os
from dotenv import load_dotenv

# Load .env file for local development (GitHub Actions injects env vars directly)
load_dotenv()

# ─── Required Secrets ───────────────────────────────────────────────────────────
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")

# ─── Agent Settings ─────────────────────────────────────────────────────────────
MAX_POSTS_PER_RUN = int(os.environ.get("MAX_POSTS_PER_RUN", "3"))
MAX_VIDEO_AGE_HOURS = int(os.environ.get("MAX_VIDEO_AGE_HOURS", "24"))

# Search queries to find trending cartoons (rotated each run for variety)
SEARCH_QUERIES = [
    "trending cartoon clips",
    "funny cartoon moments",
    "best animated videos",
    "cartoon compilation trending",
    "animation meme trending",
    "cartoon edits viral",
    "funny animation clips",
    "best cartoon scenes",
    "animated comedy viral",
    "cartoon funny compilation",
]

# ─── File Paths ──────────────────────────────────────────────────────────────────
POSTED_VIDEOS_FILE = os.path.join(os.path.dirname(__file__), "posted_videos.json")

# ─── Validation ──────────────────────────────────────────────────────────────────
def validate_config():
    """Raise an error if any required config is missing."""
    missing = []
    if not YOUTUBE_API_KEY:
        missing.append("YOUTUBE_API_KEY")
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHANNEL_ID:
        missing.append("TELEGRAM_CHANNEL_ID")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}.\n"
            f"See .env.example for the template."
        )
