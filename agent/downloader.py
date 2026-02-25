"""
Video Downloader — downloads YouTube videos using pytubefix.
"""

import logging
import os
from typing import Optional
from pytubefix import YouTube

logger = logging.getLogger(__name__)


def _sanitize_filename(title: str) -> str:
    """Remove characters that are unsafe for filenames."""
    unsafe = '<>:"/\\|?*'
    for char in unsafe:
        title = title.replace(char, "")
    return title.strip()[:80]


def download_video(video_id: str, title: str, download_dir: str) -> Optional[str]:
    """
    Download a YouTube video using pytubefix.

    Returns the path to the downloaded file, or None if download fails.
    """
    os.makedirs(download_dir, exist_ok=True)
    safe_title = _sanitize_filename(title)
    filename = f"{safe_title} [{video_id}].mp4"
    url = f"https://www.youtube.com/watch?v={video_id}"

    # Prioritized list of clients to try (MWEB is currently most resilient to bot detection)
    clients_to_try = ['MWEB', 'ANDROID', 'WEB_EMBED', 'IOS', 'WEB']

    for client_name in clients_to_try:
        try:
            logger.info(f"📥 Attempting download with {client_name} client: {title}")
            # We avoid use_po_token=True to prevent interactive prompts in headless environments
            yt = YouTube(url, client=client_name)
            stream = yt.streams.get_highest_resolution()

            if stream:
                filepath = stream.download(output_path=download_dir, filename=filename)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                logger.info(f"✅ Downloaded with {client_name}: {title} ({size_mb:.1f} MB)")
                return filepath
            else:
                logger.warning(f"⚠️ No stream found for {title} using {client_name} client.")
        except Exception as e:
            if "detected as a bot" in str(e).lower() or "403" in str(e):
                logger.warning(f"🚫 {client_name} client detected as bot/forbidden for {title}.")
            else:
                logger.warning(f"⚠️ {client_name} client error for {title}: {e}")
            continue

    # Final fallback: try without any specific client
    try:
        logger.info(f"🔄 Final fallback attempt for: {title}")
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        if stream:
            filepath = stream.download(output_path=download_dir, filename=filename)
            return filepath
    except Exception as e:
        logger.error(f"❌ All download attempts failed for '{title}': {e}")
        return None


def download_videos(videos: list, download_dir: str) -> list:
    """
    Download multiple videos. Returns video list with 'file_path' added.
    Videos that fail to download will have file_path=None.
    """
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
