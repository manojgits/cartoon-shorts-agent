"""
Video Downloader — downloads YouTube videos using yt-dlp.

YouTube requires authentication for downloads. The agent supports
browser cookies for auth. Without cookies, download may fail (403).
The agent continues gracefully, sending Telegram links without Drive links.
"""

import logging
import os
from typing import Optional
import yt_dlp

logger = logging.getLogger(__name__)


def _sanitize_filename(title: str) -> str:
    """Remove characters that are unsafe for filenames."""
    unsafe = '<>:"/\\|?*'
    for char in unsafe:
        title = title.replace(char, "")
    return title.strip()[:80]  # Limit length


def _get_cookies_path() -> Optional[str]:
    """Find cookies.txt if it exists."""
    paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies.txt"),
        os.path.expanduser("~/cookies.txt"),
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def download_video(video_id: str, title: str, download_dir: str) -> Optional[str]:
    """
    Download a YouTube video using yt-dlp.

    Returns the path to the downloaded file, or None if download fails.
    """
    os.makedirs(download_dir, exist_ok=True)
    safe_title = _sanitize_filename(title)
    output_template = os.path.join(download_dir, f"{safe_title} [{video_id}].%(ext)s")

    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 3,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
    }

    # Use cookies if available (needed for YouTube auth)
    cookies_path = _get_cookies_path()
    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path
        logger.info(f"Using cookies from: {cookies_path}")

    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            if os.path.exists(filepath):
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                logger.info(f"✅ Downloaded: {title} ({size_mb:.1f} MB)")
                return filepath
            else:
                logger.error(f"❌ File not found after download: {filepath}")
                return None
    except Exception as e:
        logger.warning(f"⚠️ Could not download '{title}': {e}")
        return None


def download_videos(videos: list, download_dir: str) -> list:
    """
    Download multiple videos. Returns video list with 'file_path' added.
    Videos that fail to download will have file_path=None.
    """
    cookies_available = _get_cookies_path() is not None
    if not cookies_available:
        logger.warning(
            "⚠️ No cookies.txt found — YouTube may block downloads. "
            "Export cookies from your browser to enable downloads. "
            "Videos will still be sent to Telegram with YouTube links."
        )

    results = []
    for video in videos:
        filepath = download_video(
            video_id=video["video_id"],
            title=video["title"],
            download_dir=download_dir,
        )
        video_with_path = dict(video)
        video_with_path["file_path"] = filepath
        results.append(video_with_path)

    downloaded = sum(1 for v in results if v["file_path"])
    logger.info(f"Downloaded {downloaded}/{len(videos)} videos successfully")
    return results
