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

# ─── Google Drive Settings ───────────────────────────────────────────────────────
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
SERVICE_ACCOUNT_FILE = os.environ.get(
    "SERVICE_ACCOUNT_FILE",
    os.path.join(os.path.dirname(__file__), "cartoon-shorts-agent-7ba69faa4235.json"),
)

# ─── Agent Settings ─────────────────────────────────────────────────────────────
NUM_SHORTS = int(os.environ.get("NUM_SHORTS", "2"))
NUM_FULL_LENGTH = int(os.environ.get("NUM_FULL_LENGTH", "2"))
MAX_VIDEO_AGE_HOURS = int(os.environ.get("MAX_VIDEO_AGE_HOURS", "24"))

# Search queries for SHORTS (≤60 seconds)
SHORTS_QUERIES = [
    "cartoon shorts trending",
    "animated shorts funny",
    "cartoon meme shorts",
    "animation shorts viral",
    "funny cartoon shorts",
]

# Search queries for FULL-LENGTH cartoon videos
FULL_LENGTH_QUERIES = [
    "trending cartoon full episode",
    "funny cartoon compilation",
    "best cartoon scenes",
    "cartoon funny moments",
    "animated comedy compilation",
    "cartoon edits viral",
]

# ─── File Paths ──────────────────────────────────────────────────────────────────
POSTED_VIDEOS_FILE = os.path.join(os.path.dirname(__file__), "posted_videos.json")
DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "downloads")

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
    if not GOOGLE_DRIVE_FOLDER_ID:
        missing.append("GOOGLE_DRIVE_FOLDER_ID")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}.\n"
            f"See .env.example for the template."
        )
