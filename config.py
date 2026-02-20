"""
Configuration module — loads all settings from environment variables.
"""

import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file for local development (GitHub Actions injects env vars directly)
load_dotenv()

# ─── Required Secrets ───────────────────────────────────────────────────────────
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")

# ─── Google Drive Settings ───────────────────────────────────────────────────────
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.json")

# ─── Gemini AI Settings ──────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ─── YouTube Upload Settings ─────────────────────────────────────────────────────
YOUTUBE_PRIVACY = os.environ.get("YOUTUBE_PRIVACY", "public")  # public, unlisted, private

# ─── Agent Settings ─────────────────────────────────────────────────────────────
NUM_SHORTS = int(os.environ.get("NUM_SHORTS", "3"))
NUM_FULL_LENGTH = int(os.environ.get("NUM_FULL_LENGTH", "1"))
MAX_VIDEO_AGE_HOURS = int(os.environ.get("MAX_VIDEO_AGE_HOURS", "24"))

# Search queries for SHORTS (≤60 seconds)
# Mix of US/UK, Europe, and India trending terms for global reach
SHORTS_QUERIES = [
    # US/UK/Europe — English cartoon trends
    "cartoon shorts trending",
    "animated shorts funny",
    "cartoon meme shorts",
    "animation shorts viral",
    "funny cartoon shorts",
    "cartoon animation meme",
    "try not to laugh cartoon shorts",
    # India — Hindi/popular cartoon shorts
    "funny cartoon shorts India",
    "cartoon shorts hindi",
    "animation meme shorts trending",
]

# Search queries for FULL-LENGTH cartoon videos
# International mix for US/UK/Europe/India audiences
FULL_LENGTH_QUERIES = [
    # US/UK/Europe — compilation & comedy
    "trending cartoon full episode",
    "funny cartoon compilation",
    "best cartoon scenes",
    "cartoon funny moments",
    "animated comedy compilation",
    "cartoon edits viral",
    # India — popular cartoon compilations
    "cartoon funny moments compilation",
    "best cartoon compilation trending",
    "funniest cartoon scenes ever",
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
    if not GEMINI_API_KEY:
        logger.warning("⚠️ GEMINI_API_KEY not set — AI thumbnails and SEO will be skipped.")
    if not os.path.exists(TOKEN_FILE):
        logger.warning("⚠️ token.json not found — Drive/YouTube upload will be skipped. Run 'python auth_setup.py' to set up.")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}.\n"
            f"See .env.example for the template."
        )
